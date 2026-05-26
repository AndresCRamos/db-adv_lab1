xquery version "3.1";

(:~ let $hr := doc("/db/lab1/data/hr_populate.xml")/HumanResources ~:)
let $hr := doc("../data/hr_populate.xml")/HumanResources

let $region_id := $hr/Regions/Region[region_name = "Americas"]/@region_id

let $country_ids := $hr/Countries/Country[@region_id = $region_id]/@country_id

let $location_ids := $hr/Locations/Location[@country_id = $country_ids]/@location_id

let $marketing_dept_ids :=
  $hr/Departments/Department[
    department_name = "Marketing" and
    @location_id = $location_ids
  ]/@department_id

return
  <Results>
  {
    for $emp in $hr/Employees/Employee[@department_id = $marketing_dept_ids]
    return
      <Employee>
        <employee_id>{ string($emp/@employee_id) }</employee_id>
        <first_name>{ string($emp/first_name) }</first_name>
        <last_name>{ string($emp/last_name) }</last_name>
        <email>{ string($emp/email) }</email>
        <department>Marketing</department>
        <region>Americas</region>
      </Employee>
  }
  </Results>
