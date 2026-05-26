xquery version "3.1";

(:~ let $hr := doc("/db/lab1/data/hr_populate.xml")/HumanResources ~:)
let $hr := doc("../data/hr_populate.xml")/HumanResources

return
  <Results>
  {
    for $region in $hr/Regions/Region
    let $country_ids := $hr/Countries/Country[@region_id = $region/@region_id]/@country_id
    let $region_locations := $hr/Locations/Location[@country_id = $country_ids]
    return
      <Region name="{ string($region/region_name) }">
        {
          for $loc in $region_locations
          let $dept_ids := $hr/Departments/Department[@location_id = $loc/@location_id]/@department_id
          let $worker_count := count($hr/Employees/Employee[@department_id = $dept_ids])
          order by $worker_count descending
          return
            <Location location_id="{ string($loc/@location_id) }" country_id="{ string($loc/@country_id) }">
              { $loc/street_address }
              { $loc/postal_code }
              { $loc/city }
              { $loc/state_province }
              <worker_count>{ $worker_count }</worker_count>
            </Location>
        }
      </Region>
  }
  </Results>