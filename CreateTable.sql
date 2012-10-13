--
-- Table `MACOUI`
--

CREATE TABLE IF NOT EXISTS `MACOUI` (
  `OUI` varchar(8) NOT NULL,
  `Organization` text NOT NULL,
  `Address` text NOT NULL,
  UNIQUE KEY `OUI` (`OUI`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;