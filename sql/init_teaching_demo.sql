-- 数据库课程实验加分项 2 演示库

CREATE DATABASE IF NOT EXISTS teaching_demo
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE teaching_demo;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS teaching_classes;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- 用户表：用于登录和角色跳转。
-- 说明：password 在本 Demo 中使用明文，便于教学演示；正式系统应保存加密后的密码。
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(30) NOT NULL UNIQUE,
  password VARCHAR(50) NOT NULL,
  role VARCHAR(20) NOT NULL,
  related_no VARCHAR(20),
  display_name VARCHAR(30) NOT NULL
);

-- 学生表：对应课程实验中的 S 表，字段做了简化。
CREATE TABLE students (
  student_no VARCHAR(20) PRIMARY KEY,
  student_name VARCHAR(30) NOT NULL,
  gender CHAR(1) NOT NULL,
  major VARCHAR(50) NOT NULL
);

-- 课程表：对应课程实验中的 C 表，供管理员课程管理 CRUD 使用。
CREATE TABLE courses (
  course_no VARCHAR(20) PRIMARY KEY,
  course_name VARCHAR(50) NOT NULL,
  credit DECIMAL(2,1) NOT NULL,
  prerequisite_no VARCHAR(20)
);

-- 教学班表：一门课程可以开多个教学班，供学生查询和选课使用。
CREATE TABLE teaching_classes (
  class_id INT PRIMARY KEY AUTO_INCREMENT,
  course_no VARCHAR(20) NOT NULL,
  teacher_no VARCHAR(20) NOT NULL,
  teacher_name VARCHAR(30) NOT NULL,
  semester VARCHAR(20) NOT NULL,
  class_name VARCHAR(30) NOT NULL,
  capacity INT NOT NULL,
  selected_count INT NOT NULL DEFAULT 0,
  class_time VARCHAR(50) NOT NULL,
  classroom VARCHAR(30) NOT NULL,
  CONSTRAINT fk_class_course
    FOREIGN KEY (course_no) REFERENCES courses(course_no)
    ON DELETE CASCADE,
  CONSTRAINT chk_class_capacity
    CHECK (capacity >= 0 AND selected_count >= 0 AND selected_count <= capacity)
);

-- 选课表：对应课程实验中的 SC 表，增加 class_id 表示选的是哪个教学班。
CREATE TABLE enrollments (
  enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
  student_no VARCHAR(20) NOT NULL,
  class_id INT NOT NULL,
  grade DECIMAL(5,2),
  selected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_student_class UNIQUE (student_no, class_id),
  CONSTRAINT fk_enrollment_student
    FOREIGN KEY (student_no) REFERENCES students(student_no)
    ON DELETE CASCADE,
  CONSTRAINT fk_enrollment_class
    FOREIGN KEY (class_id) REFERENCES teaching_classes(class_id)
    ON DELETE CASCADE
);

INSERT INTO users (username, password, role, related_no, display_name) VALUES
  ('admin', '123456', 'admin', NULL, '系统管理员'),
  ('stu001', '123456', 'student', 'S001', '张三'),
  ('stu002', '123456', 'student', 'S002', '李四'),
  ('teacher001', '123456', 'teacher', 'T001', '王老师');

INSERT INTO students (student_no, student_name, gender, major) VALUES
  ('S001', '张三', '男', '计算机科学与技术'),
  ('S002', '李四', '女', '软件工程'),
  ('S003', '王五', '男', '数据科学与大数据技术'),
  ('S004', '赵六', '女', '人工智能');

INSERT INTO courses (course_no, course_name, credit, prerequisite_no) VALUES
  ('C001', '数据库原理', 3.0, NULL),
  ('C002', '数据结构', 4.0, NULL),
  ('C003', '操作系统', 4.0, 'C002'),
  ('C004', 'Web应用开发', 2.0, NULL),
  ('C005', '人工智能导论', 2.0, NULL);

INSERT INTO teaching_classes
  (course_no, teacher_no, teacher_name, semester, class_name, capacity, selected_count, class_time, classroom)
VALUES
  ('C001', 'T001', '王老师', '2026春', '01班', 3, 1, '周一 1-2节', '一教101'),
  ('C001', 'T002', '李老师', '2026春', '02班', 1, 1, '周三 3-4节', '一教102'),
  ('C002', 'T003', '张老师', '2026春', '01班', 2, 1, '周二 5-6节', '二教201'),
  ('C003', 'T004', '赵老师', '2026春', '01班', 2, 1, '周四 1-2节', '二教301'),
  ('C004', 'T001', '王老师', '2026春', '01班', 3, 1, '周五 3-4节', '实验楼501'),
  ('C005', 'T005', '陈老师', '2026秋', '01班', 2, 0, '周二 7-8节', '三教203');

INSERT INTO enrollments (student_no, class_id, grade) VALUES
  ('S001', 1, 88.00),
  ('S001', 3, NULL),
  ('S002', 2, 91.00),
  ('S003', 4, 76.00),
  ('S004', 5, NULL);

-- 常用演示查询 1：学生可选课程列表。
SELECT
  tc.class_id,
  c.course_no,
  c.course_name,
  c.credit,
  tc.teacher_name,
  tc.semester,
  tc.class_name,
  tc.capacity,
  tc.selected_count,
  tc.class_time,
  tc.classroom
FROM teaching_classes tc
JOIN courses c ON tc.course_no = c.course_no
ORDER BY tc.class_id;

-- 常用演示查询 2：某个学生已选课程。
SELECT
  s.student_no,
  s.student_name,
  c.course_name,
  tc.teacher_name,
  tc.semester,
  tc.class_time,
  e.grade
FROM enrollments e
JOIN students s ON e.student_no = s.student_no
JOIN teaching_classes tc ON e.class_id = tc.class_id
JOIN courses c ON tc.course_no = c.course_no
WHERE s.student_no = 'S001';
