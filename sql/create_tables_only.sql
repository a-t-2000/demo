-- =====================================================
-- База данных "Корочки.есть"
-- Только создание таблиц
-- =====================================================

CREATE DATABASE IF NOT EXISTS korochki_net;
USE korochki_net;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS statuses;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- Таблицы-справочники
-- =====================================================

-- Таблица ролей пользователей
CREATE TABLE roles (
    id_role INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID роли',
    role_name VARCHAR(50) NOT NULL UNIQUE COMMENT 'Название роли'
) COMMENT 'Роли пользователей системы';

-- Таблица статусов заявок
CREATE TABLE statuses (
    id_status INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID статуса',
    status_name VARCHAR(50) NOT NULL UNIQUE COMMENT 'Название статуса'
) COMMENT 'Статусы заявок';

-- =====================================================
-- Основные таблицы
-- =====================================================

-- Таблица пользователей
CREATE TABLE users (
    id_user INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID пользователя',
    last_name VARCHAR(100) NOT NULL COMMENT 'Фамилия',
    first_name VARCHAR(100) NOT NULL COMMENT 'Имя',
    middle_name VARCHAR(100) COMMENT 'Отчество',
    login VARCHAR(100) NOT NULL UNIQUE COMMENT 'Логин',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Хэш пароля',
    phone VARCHAR(20) NOT NULL COMMENT 'Телефон',
    email VARCHAR(100) NOT NULL COMMENT 'Электронная почта',
    id_role INT NOT NULL COMMENT 'ID роли',

    FOREIGN KEY (id_role) REFERENCES roles(id_role) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_login (login),
    INDEX idx_last_name (last_name),
    INDEX idx_first_name (first_name),
    INDEX idx_full_name (last_name, first_name, middle_name)
) COMMENT 'Пользователи системы';

-- Таблица заявок
CREATE TABLE applications (
    id_application INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID заявки',
    id_user INT NOT NULL COMMENT 'ID пользователя',
    course_name VARCHAR(255) NOT NULL COMMENT 'Название курса',
    start_date DATE NOT NULL COMMENT 'Желаемая дата начала',
    payment_method VARCHAR(50) NOT NULL COMMENT 'Способ оплаты',
    review TEXT COMMENT 'Отзыв',
    id_status INT NOT NULL COMMENT 'ID статуса заявки',

    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_status) REFERENCES statuses(id_status) ON DELETE RESTRICT ON UPDATE CASCADE,

    INDEX idx_user (id_user),
    INDEX idx_status (id_status)
) COMMENT 'Заявки на обучение';

SELECT 'Tables created successfully!' as status;