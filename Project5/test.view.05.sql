1: CREATE TABLE names (name TEXT, id INTEGER);
1: INSERT INTO names VALUES ('James', 1), ('Yaxin', 2), ('Li', 3), ('Robert', 4);
1: CREATE TABLE grades (grade REAL, id INTEGER);
1: INSERT INTO grades VALUES (2.4, 1), (3.5, 2), (3.7, 3), (4.0, 4);
1: SELECT names.name, grades.grade FROM names LEFT OUTER JOIN grades ON names.id = grades.id ORDER BY names.id;
1: CREATE VIEW stu_view AS SELECT names.name, grades.grade FROM names LEFT OUTER JOIN grades ON names.id = grades.id ORDER BY names.id;
1: SELECT * FROM stu_view ORDER BY name;
1: SELECT grade FROM stu_view ORDER BY name;
