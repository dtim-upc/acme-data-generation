-- R16: flightID is an identifier of Flights.
select count(distinct flightID), count(*) from flights f;

--  R17: flightID is derived by concatenating the following values: Date-Origin-Destination-FlightNumber-AircraftRegistration (lengths: 6+1+3+1+3+1+4+1+6=26). 
	-- 3273 with wrong date out of 50000
select count(*) from flights f
where substring(flightID,0,7) <> to_char(f.scheduleddeparture, 'DDMMYY');
select count(*) from flights f
where substring(flightID,0,7) = to_char(f.scheduleddeparture, 'DDMMYY');

	-- 0 with wrong origin or destination airport
select count(*) from flights f
where substring(flightID,8,3) <> departureairport or substring(flightID,12,3) <> arrivalairport

	--(5527 with some error out of 50000)
select count(*) from flights f
where substring(flightID,21,6) <> f.aircraftregistration or 
      substring(flightID,0,7) <> to_char(f.scheduleddeparture, 'DDMMYY') or 
      substring(flightID,8,3) <> departureairport or substring(flightID,12,3) <> arrivalairport;

-- R18: delayCode in OperationInterruption is a 2 digits IATA code 2
	-- 2986 out of 500000 rows with delaycode null and with actual delay. 
select count(*) from flights f 
where delaycode is null and actualarrival::timestamp > scheduledarrival::timestamp; 


--  R19: In a Slot, scheduledArrival must be posterior to the scheduledDeparture.
	-- 13 with error, out of 100000
select count(*) from slots s
where scheduledarrival::timestamp  <= scheduleddeparture::timestamp ;

--  R20: Two Slots of the same aircraft cannot overlap in time. Here we assume it refers to flight slots.
	-- 24991 with overlaps out of 50000 
select count(distinct f1.flightid) from flights f1, flights f2
where f1.aircraftregistration = f2.aircraftregistration and
     ((f1.actualdeparture, f1.actualarrival) overlaps (f2.actualdeparture, f2.actualarrival)) and
     ((f1.scheduleddeparture, f1.scheduledarrival) overlaps (f2.scheduleddeparture, f2.scheduledarrival));
  
-- R21: In Flights, departure and arrival airports must be those in the flightID (unless this flight has been diverted)
	-- no additional info if the flight is diverted
select count(*) from flights f
where substring(flightID,8,3) <> departureairport or substring(flightID,12,3) <> arrivalairport      

-- R22: In a Flight, actualArrival is posterior to actualDeparture.
	-- 926 with error, out of 50000
select count(*) from flights f
where actualarrival::timestamp  < actualdeparture::timestamp ;


select scheduledarrival, scheduleddeparture, scheduledarrival-scheduleddeparture 
from flights f where date_part('day', age(scheduledarrival, scheduleddeparture))>1 
order by scheduledarrival-scheduleddeparture asc

select count(*) from flights f 
where age(scheduledarrival, scheduleddeparture) < interval '20' minute 


select actualarrival, actualdeparture, actualarrival-actualdeparture 
from flights f where date_part('day', age(actualarrival, actualdeparture))>1 
order by actualarrival-actualdeparture asc

select count(*) from flights f 
where age(actualarrival , actualdeparture) < interval '20' minute  

-- programmed vs non-programmed half-half
select count(*) from maintenance m 
where programmed  = false


