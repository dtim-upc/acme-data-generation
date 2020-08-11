# What

It was hard to understand the relationship between these two, so I will summarize here what I know about it.

- Both share a `kind` attribute, that can be any of these:

```python
["Delay",
"Safety",
"AircraftOnGround",
"Maintenance",
"Revision",]
```

![picture 1](./images/70074115bb8f31767958b484da7a96badaac7708209c1693398df072b7baaf41.png)

Although this is not implemented in the SQL tables, in this case, we see that there are
two types of maintenance events

- OI events: _Delay_, _Safety_
- AOS events: _Aircraft on ground_, _Maintenance_, _Revision_

In SQL, however, only an OI table is implemented
![picture 2](./images/099705e98ba61f68f438251384053c9b9eb7f608e105d3cbd9f3c95ff6b870d5.png)

So it is safe to assume that _all_ maintenance events are stored in this table, and those
that are of type _delay_ or _safety_ are replicated in the OI table.

In other words,

- _flight_slots_ produce *operational interruptions* events, which are stored in the OI table
- _maintenance slots_ produce *aircraft out of service* events, which are stored in the MaintenanceEvents table
- the *maintenance events* table stores both OI and AOS instances
