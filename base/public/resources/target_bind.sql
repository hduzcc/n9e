UPDATE target AS p
JOIN (
    SELECT b.tid, c.busi_group_id
    FROM (
        SELECT aa.tid, aa.ugid, aa.note
        FROM (
            SELECT target.id AS tid, user_group.id AS ugid, LENGTH(user_group.note) AS note
            FROM target
            LEFT JOIN user_group ON target.ident LIKE CONCAT(user_group.note, "%")
            WHERE target.group_id = 0 AND user_group.note != ""
        ) AS aa
        INNER JOIN (
            SELECT a.tid, MAX(note) AS note
            FROM (
                SELECT target.id AS tid, user_group.id AS ugid, LENGTH(user_group.note) AS note
                FROM target
                LEFT JOIN user_group ON target.ident LIKE CONCAT(user_group.note, "%")
                WHERE target.group_id = 0 AND user_group.note != ""
            ) AS a
            GROUP BY a.tid
        ) AS bb ON aa.tid = bb.tid AND aa.note = bb.note
    ) AS b
    LEFT JOIN busi_group_member as c ON b.ugid = c.user_group_id
) AS pp ON p.id = pp.tid
SET p.group_id = pp.busi_group_id;