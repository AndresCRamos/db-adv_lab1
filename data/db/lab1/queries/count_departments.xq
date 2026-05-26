xquery version "3.1";

(:~ let $hr := doc("/db/lab1/data/hr_populate.xml")/HumanResources ~:)
let $hr := doc("../data/hr_populate.xml")/HumanResources

return
  <Results>
  {
    for $dept in $hr/Departments/Department
    let $count := count($hr/Employees/Employee[@department_id = $dept/@department_id])
    order by $dept/department_name
    return
      <Department>
        <department_id>{ string($dept/@department_id) }</department_id>
        <department_name>{ string($dept/department_name) }</department_name>
        <employee_count>{ $count }</employee_count>
      </Department>
  }
  </Results>