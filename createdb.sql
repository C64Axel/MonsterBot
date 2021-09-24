CREATE DATABASE `tgbotdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE tgbotdb;

CREATE TABLE `bot` (
	`botid` int(11) NOT NULL,
	`botname` varchar(45) NOT NULL,
	PRIMARY KEY (`botid`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user` (
	`botid` int(11) NOT NULL,
	`username` varchar(45) DEFAULT NULL,
	`vorname` varchar(45) DEFAULT NULL,
	`nachname` varchar(45) DEFAULT NULL,
	`chatid` varchar(45) NOT NULL,
	`lastchange` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`lat` double DEFAULT 0,
	`lon` double DEFAULT 0,
	`dist` double DEFAULT 0,
	PRIMARY KEY (`chatid`,`botid`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE userstop (
	`chatid` varchar(45) NOT NULL,
	`stopdate` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`chatid`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE userblock (
	`chatid` varchar(45) NOT NULL,
	PRIMARY KEY (`chatid`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE userallow (
	`chatid` varchar(45) NOT NULL,
	PRIMARY KEY (`chatid`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `userassign` (
	`pkmnid` int(11) NOT NULL,
	`chatid` varchar(45) NOT NULL,
	`iv` int(11) NOT NULL DEFAULT '0',
	`level` int(11) NOT NULL DEFAULT '0',
	PRIMARY KEY (`pkmnid`,`chatid`),
	KEY `pkmnid_idx` (`pkmnid`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dbversion` (
	`version` int(11) NOT NULL DEFAULT '0',
	PRIMARY KEY (`version`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
insert into dbversion values ( "3" );
