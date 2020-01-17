CREATE DATABASE IF NOT EXISTS `ais` DEFAULT CHARACTER SET utf8;

CREATE TABLE IF NOT EXISTS `ais`.`stock` (
    `id` VARCHAR(10) NOT NULL,
    `name` VARCHAR(32) NOT NULL,
    `updated_date` date NOT NULL,
    `now_price` FLOAT(11,2) NOT NULL COMMENT '当前价格',
    `open_price` FLOAT(11,2) NOT NULL COMMENT '开盘价格',
    `close_price` FLOAT(11,2) NOT NULL COMMENT '昨日封盘价格',
    `high_price` FLOAT(11,2) NOT NULL COMMENT '最高价格',
    `low_price` FLOAT(11,2) NOT NULL COMMENT '最低价格',
    `high_limit` FLOAT(11,2) NOT NULL COMMENT '涨停价格',
    `low_limit` FLOAT(11,2) NOT NULL COMMENT '跌停价格',
    `changes` FLOAT(11,2) NOT NULL COMMENT '涨跌',
    `rate` FLOAT(5,2) NOT NULL COMMENT '涨跌幅',
    `volume` INT NOT NULL COMMENT '成交量',
    `amount` INT NOT NULL COMMENT '成交金额',
    `swap_rate` FLOAT(5,2) NOT NULL COMMENT '换手率',
    `per` FLOAT(11,2) NOT NULL COMMENT '市盈率',
    `amplitude` FLOAT(11,2) NOT NULL COMMENT '振幅',
    `market_value` FLOAT(11,2) NOT NULL COMMENT '流通市值',
    `total_value` FLOAT(11,2) NOT NULL COMMENT '总市值',
    `qrr` FLOAT(11,2) NOT NULL COMMENT '量比',
    `pbr` FLOAT(11,2) NOT NULL COMMENT '市净率',
    `buy_price` FLOAT(11,2) NOT NULL COMMENT '买一价格',
    `buy_count` INT NOT NULL COMMENT '买一数量',
    `sold_price` FLOAT(11,2) NOT NULL COMMENT '卖一价格',
    `sold_count` INT NOT NULL COMMENT '卖一数量',
    `big_in_1` FLOAT(11,2) NOT NULL COMMENT '今日大单流入',
    `big_in_2` FLOAT(11,2) NOT NULL COMMENT '前1日大单流入',
    `big_in_3` FLOAT(11,2) NOT NULL COMMENT '前2日大单流入',
    `big_in_4` FLOAT(11,2) NOT NULL COMMENT '前3日大单流入',
    `big_in_5` FLOAT(11,2) NOT NULL COMMENT '前4日大单流入',
    `big_out_1` FLOAT(11,2) NOT NULL COMMENT '今日大单流出',
    `big_out_2` FLOAT(11,2) NOT NULL COMMENT '前1日大单流出',
    `big_out_3` FLOAT(11,2) NOT NULL COMMENT '前2日大单流出',
    `big_out_4` FLOAT(11,2) NOT NULL COMMENT '前3日大单流出',
    `big_out_5` FLOAT(11,2) NOT NULL COMMENT '前4日大单流出',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE IF NOT EXISTS `ais`.`user` (
    `id` VARCHAR(16) NOT NULL,
    `password` VARCHAR(16) NOT NULL,
    `level` INT NOT NULL COMMENT '0-free 1-normal 2-vip',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

CREATE TABLE IF NOT EXISTS `ais`.`self_stock` (
    `id` VARCHAR(16) NOT NULL,
    `user_id` VARCHAR(16) NOT NULL,
    `stock_id` VARCHAR(10) NOT NULL,
    `hold_count` INT NOT NULL,
    `buy_price` FLOAT(11,2) NOT NULL,
    `buy_date` date NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;