select 'organizations' as relation_name, count(*) as row_count from public.organizations
union all select 'people', count(*) from public.people
union all select 'academic_sessions', count(*) from public.academic_sessions
union all select 'courses', count(*) from public.courses
union all select 'classes', count(*) from public.classes
union all select 'enrollments', count(*) from public.enrollments
union all select 'line_items', count(*) from public.line_items
union all select 'results', count(*) from public.results
union all select 'source_identifiers', count(*) from public.source_identifiers
order by relation_name;

select class_title, display_name, class_role
from public.class_roster
order by class_title, class_role, display_name;

select class_title, line_item_title, learner_name, score_status, score
from public.gradebook_results
order by class_title, line_item_title, learner_name;
