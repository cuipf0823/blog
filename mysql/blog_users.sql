ßßß/*
Navicat MySQL Data Transfer

Source Server         : 10.1.1.119ru
Source Server Version : 50544
Source Host           : 10.1.1.119:3306
Source Database       : ru_1001

Target Server Type    : MYSQL
Target Server Version : 50544
File Encoding         : 65001

Date: 2017-01-06 16:50:32
*/

SET FOREIGN_KEY_CHECKS=0;
-- ----------------------------
-- Table structure for `blog_users`
-- ----------------------------
DROP TABLE IF EXISTS `blog_users`;
CREATE TABLE `blog_users` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT,
  `user_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `pwd_hash` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `email` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `role_id` int(32) NOT NULL,
  `reg_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_name` (`user_name`),
  UNIQUE KEY `idx_email` (`email`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of blog_users
-- ----------------------------
INSERT INTO blog_users VALUES ('19', 'cuipf1989', 'pbkdf2:sha1:1000$iZxWqFPh$61757e1bbe6aeaad72b6f0e2ffa87c3e5374661e', '570094028@qq.com', '0', '2017-01-06 16:23:12');
INSERT INTO blog_users VALUES ('20', 'cuipf', 'pbkdf2:sha1:1000$y3Uer6Rd$8c293ad927196d9fca6d518b9a62cf80408d67d5', 'cuipf0823@163.com', '0', '2017-01-06 16:25:17');
