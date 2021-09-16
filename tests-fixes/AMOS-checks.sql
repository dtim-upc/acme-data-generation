-- R1: workPackageID is an identifier of WorkPackage.
  -- 94370 out of 100000 are unique
select count(distinct wp.workpackageid), count(*) from workpackages wp;
	-- fixes
	-- update all duplicates to the same value
	update workpackages wp1 set workpackageid = 50001
	where not exists (select wp2.workpackageid, count(*) from workpackages wp2 where wp1.workpackageid  = wp2.workpackageid  group by WP2.workpackageid having COUNT(*)<=1); 
	
	-- update all duplicates of the saem value to that value plus rowid (ctid)
	update workpackages wp1 set workpackageid = 50001+CONCAT((ctid::text::point)[0],'0',(ctid::text::point)[1])::bigint --floor(random()*(100000-50001+1))+50001
	where wp1.workpackageid = 50001

-- R2: workOrderID is an identifier of WorkOrders/ForecastedOrders/TechnicalLogBookOrders.
select count(distinct wo.workorderid), count(*) from workorders wo;
	-- fixes
	-- update all duplicates to the same value
	update workorders wp1 set workorderid = 50001
	where not exists (select wp2.workorderid, count(*) from workorders wp2 where wp1.workorderid  = wp2.workorderid  group by WP2.workorderid having COUNT(*)<=1); 
	
	-- update all duplicates of the saem value to that value plus rowid (ctid)
	update workorders wp1 set workorderid = 50001+CONCAT((ctid::text::point)[0],'0',(ctid::text::point)[1])::bigint --floor(random()*(100000-50001+1))+50001
	where wp1.workorderid = 50001

-- check if workpackage from workorders references workpackageID
select count(*) from workorders wo
where not exists (select * from workpackages wp where wo.workpackage = wp.workpackageid);	
	-- fix set FK to random PK of another table
	update workorders set workpackage =  (SELECT wp.workpackageid FROM workpackages wp                
				                 ORDER BY random()+CONCAT((ctid::text::point)[0],'0',(ctid::text::point)[1])::bigint LIMIT 1)


				                 	

-- R3: maintenanceID is an identifier of MaintenanceEvents/OperationInterruption.
select count(distinct me.maintenanceid), count(*) from MaintenanceEvents me
select count(oi.maintenanceid), count(*) from OperationInterruption oi
	-- fixes
	-- update all duplicates to the same value
	update MaintenanceEvents wp1 set maintenanceid = 50001
	where not exists (select wp2.maintenanceid, count(*) from MaintenanceEvents wp2 where wp1.maintenanceid  = wp2.maintenanceid  group by WP2.maintenanceid having COUNT(*)<=1); 
	
	-- update all duplicates of the saem value to that value plus rowid (ctid)
	update MaintenanceEvents wp1 set maintenanceid = 50001+CONCAT((ctid::text::point)[0],'0',(ctid::text::point)[1])::bigint --floor(random()*(100000-50001+1))+50001
	where wp1.maintenanceid = 50001

	
-- R4: file is an identifier of Attachments.
select count(distinct me.file), count(*) from Attachments  me	

-- R5: event of an Attachment is a reference to maintenanceID of MaintenanceEvents. (Attachments->MaintenanceEvents)
select count(*) from attachments a
where not exists (select * from maintenanceevents m2 where maintenanceid = a."event");
-- fix update event with changes IDs from MaintenanceEvents
update attachments set event =  (SELECT e.maintenanceid FROM maintenanceevents e                
				                 ORDER BY random()+CONCAT((ctid::text::point)[0],'0',(ctid::text::point)[1])::bigint LIMIT 1)


				                 
-- R6: subsystem of MaintenanceEvents should be a 4 digits ATA code. See ATA codes for commercial aircrafts in
select count(*) from maintenanceevents m where char_length(m.subsystem)<>4;

-- R7: delayCode of OperationInterruption should be a 2 digits IATA code. See https://en.wikipedia.org/wiki/IATA_delay_codes
select count(*) from OperationInterruption oi where char_length(oi.delaycode)=2;


-- R9: ReportKind values “PIREP” and “MAREP” refer to pilot and maintenance personnel as reporters, respectively.
select count(distinct reporteurid) from TechnicalLogBookOrders tbo where reporteurclass = 'PIREP'
select distinct reporteurid from TechnicalLogBookOrders tbo where reporteurclass = 'PIREP'

-- R10: MELCathegory values A,B,C,D refer to 3,10,30,120 days of allowed delay in the repairing of the problem in the aircraft, respectively.
select count(*) 
from technicallogbookorders t
where MEL='A' and date_part('day',age(executiondate,due))>=-3;

select count(*) 
from technicallogbookorders t
where MEL='B' and date_part('day',age(executiondate,due))>=-10;

select count(*) 
from technicallogbookorders t
where MEL='C' and date_part('day',age(executiondate,due))>=-30;

select count(*) 
from technicallogbookorders t
where MEL='D' and date_part('day',age(executiondate,due))>=-120;

-- R11: airport in MaintenanceEvents must have a value.
select count(*) from maintenanceevents m where m.airport is null;

-- R12: In OperationInterruption, departure must coincide with the date of the flightID (see below how it is composed).
	-- 3273 out of 50000 with error 
select count(*)  from operationinterruption o2
where substring(o2.flightID,0,7) <> to_char(o2.departure, 'DDMMYY');


-- R13: The flight registered in OperationInterruption, must exist in the Flights of AIMS database, 
-- and be marked as “delayed” (i.e., delayCode is not null) with the same IATA delay code.
-- in a separate file!

-- R14: In MaintenanceEvents, the events of kind Maintenance that correspond to a Revision (event.kind == "Revision"),
-- are those of the same aircraft AND whose interval is completely included in that of the Revision. 
-- For all of them, the airport must be the same.
-- 2006 out of ~30000 events of type maintenance are with errors
select count(*) from maintenanceevents m
where kind = 'Maintenance' and 
not exists (select * from maintenanceevents m2 
            where m2.kind = 'Revision' and m.aircraftregistration = m2.aircraftregistration and m.airport = m2.airport
                  and m.starttime >= m2.starttime and
                  (m.starttime + m.duration) <= (m2.starttime + m2.duration))

    -- fix: set all the maintenance that belong to revision to have the same airport
update maintenanceevents m set airport = (select m2.airport from maintenanceevents m2 
            where m2.kind = 'Revision' and m.aircraftregistration = m2.aircraftregistration 
            and m.starttime::timestamp > m2.starttime::timestamp and
                  (m.starttime::timestamp + m.duration) < (m2.starttime::timestamp + m2.duration)
                  ORDER BY random()+m.maintenanceid 
                  limit 1)
           where m.kind = 'Maintenance'
           
-- In MaintenanceEvents, the events of kind Maintenance cannot partially intersect 
-- that of a Revision of the same aircraft. 
--  9051 out of 30366 of 'Maintanance' events are with error (partially overlapping periods)     
select count(*) from maintenanceevents m
where kind = 'Maintenance' and 
exists (select * from maintenanceevents m2 
            where m2.kind = 'Revision' 
            and m.aircraftregistration = m2.aircraftregistration --and m.airport = m2.airport 
            and ((m.starttime < m2.starttime and (m.starttime + m.duration) > m2.starttime and (m.starttime + m.duration) < (m2.starttime + m2.duration)) or
                 (m.starttime > m2.starttime and m.starttime < (m2.starttime + m2.duration) and (m.starttime + m.duration) > (m2.starttime + m2.duration))))
                  

--  R15: In MaintenanceEvents, maintenance duration must have the expected length according to the kind of maintenance:                 

-- 'Maintenance'  640 out of 30366 with wrong duration
select count(*) from maintenanceevents m2
where m2.kind='Maintenance' and (m2.duration < '1 hours'::interval or m2.duration > '1 days'::interval)

-- 'Revision' 7274 out of 29752 with worng duration
select count(*) from maintenanceevents m2
where m2.kind='Revision' and (m2.duration <= '1 days'::interval or m2.duration > '1 month'::interval)

-- 'Delay' 0 out of 29886 with worng duration
select count(*) from maintenanceevents m2
where m2.kind='Delay' and (m2.duration < '1 minutes'::interval or m2.duration > '60 minutes'::interval)

-- 'AircraftOnGround' 0 out of 29885 with worng duration
select count(*) from maintenanceevents m2
where m2.kind='AircraftOnGround' and (m2.duration < '1 hours'::interval or m2.duration > '24 hours'::interval)

-- fix: set a random interval in the given range to a duration
update maintenanceevents set duration = (select justify_interval(random() * (interval '24 hours' - interval '1 hours' + interval '1 hours') + interval '1 hours') 
										 from generate_series(1, 200)
                                         ORDER BY random() +  EXTRACT(EPOCH FROM NOW()) * 1000
                                         limit 1)
where kind='AircraftOnGround';


	  
-- R23: In a Maintenance Slot, the corresponding events must exist in AMOS maintenance events, inside the corresponding time interval.
-- use maintenance file to create and load temp maintenance table in AMOS and then execute check 
-- IMPORTANT: drop Maintenance table after finish               
-- 2025 out of 50000 with departure date out of the time interval of maintenance event
select count(*) from maintenance m 
where not exists (select * from maintenanceevents m2 where m.aircraftregistration = m2.aircraftregistration and
                           m.scheduleddeparture = m2.starttime and m.scheduledarrival = (m2.starttime+m2.duration))

                           
-- check if execution date in forecastedorders and technicallogbookorders are inside the range of planned and deadline and reporting and due, respectively.                           
select executiondate, deadline, planned, date_part('day', age(executiondate,deadline)), date_part('day', age(executiondate,planned)) 
from forecastedorders 
where not executiondate between planned and deadline 
order by case when abs(date_part('day', age(executiondate,deadline))) < abs(date_part('day', age(executiondate,planned))) then abs(date_part('day', age(executiondate,deadline))) else abs(date_part('day', age(executiondate,planned))) end desc;                           

select executiondate, reportingDate, due, date_part('day', age(due)), date_part('day', age(executiondate,reportingDate)) 
from technicallogbookorders t
where not executiondate between reportingDate and due and "deferred" <> true
order by case when abs(date_part('day', age(executiondate,due))) < abs(date_part('day', age(executiondate,reportingDate))) then abs(date_part('day', age(executiondate,due))) else abs(date_part('day', age(executiondate,reportingDate))) end desc;

-- fix: set execution date to a random timestamp between reporting date and due
update technicallogbookorders t set executiondate = t.reportingDate::timestamp + random()*(t.due::timestamp-t.reportingDate::timestamp)
where not executiondate between reportingDate and due 			

update technicallogbookorders t set reportingdate = (t.executiondate::timestamp - interval '1 day') + random()*(t.reportingDate::timestamp-(t.reportingDate::timestamp - interval '1 day'))
where not executiondate between reportingDate and due

update technicallogbookorders t set executiondate = (t.due::timestamp + interval '1 day') + random()*((t.due::timestamp + interval '3 day')- t.due::timestamp+ interval '1 day')
where t.mel = 'A' and t."deferred" = true

update technicallogbookorders t set executiondate = (t.due::timestamp + interval '1 day') + random()*((t.due::timestamp + interval '10 day')- t.due::timestamp+ interval '1 day')
where t.mel = 'B' and t."deferred" = true

update technicallogbookorders t set executiondate = (t.due::timestamp + interval '1 day') + random()*((t.due::timestamp + interval '30 day')- t.due::timestamp+ interval '1 day')
where t.mel = 'C' and t."deferred" = true

update technicallogbookorders t set executiondate = (t.due::timestamp+ interval '1 day') + random()*((t.due::timestamp + interval '120 day')- t.due::timestamp+ interval '1 day')
where t.mel = 'D' and t."deferred" = true



update forecastedorders t set planned = (t.executiondate::timestamp - interval '1 day') + random()*(t.executiondate::timestamp-(t.executiondate::timestamp - interval '1 day'))
where not executiondate between planned and deadline

update forecastedorders t set deadline = (t.executiondate::timestamp) + random()*((t.executiondate::timestamp + interval '7 day')- t.executiondate::timestamp)
where not executiondate between planned and deadline



-- check if all work orders exec date belong to a maintenance event (red relationship!)
select count(*) from workorders w
where not exists (select * from maintenanceevents m2 
                  where m2.aircraftregistration = w.aircraftregistration and m2.airport = w.executionplace
                        and w.executiondate > m2.starttime and w.executiondate < m2.starttime+m2.duration)
             
-- fix: assign to work orders execution date that fells inside the time interval of some maintenance event (for the same airport and the same aircraft)
update workorders w set executiondate = (select m2.starttime +
								       random() * ((m2.starttime+m2.duration) -
					                   m2.starttime) from maintenanceevents m2 					          
					                   --where m2.aircraftregistration = w.aircraftregistration and m2.airport = w.executionplace
					                   order by random() + w.workorderid limit 1)		
where not exists (select * from maintenanceevents m2 
                  where m2.aircraftregistration = w.aircraftregistration and m2.airport = w.executionplace
                        and w.executiondate > m2.starttime and w.executiondate < m2.starttime+m2.duration)
                        

SELECT distinct w.aircraftregistration FROM workorders w order by 1                        

SELECT t.reporteurid, t.executionplace FROM technicallogbookorders t 
where t.reporteurclass = 'PIREP'
group by t.reporteurid, t.executionplace 
order by 1

select count(*) from technicallogbookorders t2 
update technicallogbookorders t set executionplace = (select t1.executionplace from technicallogbookorders t1 where t1.reporteurid = t.reporteurid order by 1 limit 1)
where t.reporteurclass = 'PIREP' 

create index tindex on technicallogbookorders(reporteurid)

                        

