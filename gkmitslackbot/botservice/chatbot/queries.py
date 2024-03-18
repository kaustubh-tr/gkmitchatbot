GET_EMPLOYEE_BY_SKILL_QUERY=''' 
    SELECT e."first_name", e."last_name", e."is_remote_employee", s."skill_name", es."skill_proficiency", e."job_level", e."designation", e."job_description"
    FROM botservice_empskill es
    JOIN botservice_employee e ON es."employee_id_id" = e."id"
    JOIN botservice_skill s ON es."skill_id_id" = s."id"
    WHERE LOWER(s."skill_name") = LOWER('{skill}')
    AND e."id" != '{employee_id}'
    ORDER BY
        CASE es."skill_proficiency"
            WHEN 'Expert' THEN 1
            WHEN 'Intermediate' THEN 2
            WHEN 'Beginner' THEN 3
            ELSE 4
        END
    LIMIT 3;
    '''

SKILL_EXISTS_QUERY='''
    SELECT EXISTS(
        SELECT 1 
        FROM botservice_skill s
        JOIN botservice_empskill es ON s.id = es.skill_id_id
        WHERE LOWER(s."skill_name") = LOWER('{skill}')
        AND es."employee_id_id" != '{employee_id}'
    )
'''
