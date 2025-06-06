CREATE TABLE playerStatsPerGame (
  "season_year" VARCHAR(30) NOT NULL,
  "player_id" INTEGER NOT NULL,
  "player_name" VARCHAR(30) NOT NULL,
  "nickname" VARCHAR(30) NOT NULL,
  "team_id" INTEGER NOT NULL,
  "team_abbreviation" VARCHAR(30) NOT NULL,
  "team_name" VARCHAR(30) NOT NULL,
  "game_id" VARCHAR(30) NOT NULL,
  "game_date" VARCHAR(30) NOT NULL,
  "matchup" VARCHAR(30) NOT NULL,
  "wl" VARCHAR(30) NOT NULL,
  "min" DOUBLE PRECISION NOT NULL,
  "fgm" INTEGER NOT NULL,
  "fga" INTEGER NOT NULL,
  "fg_pct" DOUBLE PRECISION,
  "fg3m" INTEGER NOT NULL,
  "fg3a" INTEGER NOT NULL,
  "fg3_pct" DOUBLE PRECISION,
  "ftm" INTEGER NOT NULL,
  "fta" INTEGER NOT NULL,
  "ft_pct" DOUBLE PRECISION,
  "oreb" INTEGER NOT NULL,
  "dreb" INTEGER NOT NULL,
  "reb" INTEGER NOT NULL,
  "ast" INTEGER NOT NULL,
  "tov" INTEGER NOT NULL,
  "stl" INTEGER NOT NULL,
  "blk" INTEGER NOT NULL,
  "blka" INTEGER NOT NULL,
  "pf" INTEGER NOT NULL,
  "pfd" INTEGER NOT NULL,
  "pts" INTEGER NOT NULL,
  "plus_minus" INTEGER,
  "nba_fantasy_pts" DOUBLE PRECISION,
  "dd2" INTEGER,
  "td3" INTEGER,
  "wnba_fantasy_pts" DOUBLE PRECISION,
  "gp_rank" INTEGER,
  "w_rank" INTEGER,
  "l_rank" INTEGER,
  "w_pct_rank" INTEGER,
  "min_rank" INTEGER,
  "fgm_rank" INTEGER,
  "fga_rank" INTEGER,
  "fg_pct_rank" INTEGER,
  "fg3m_rank" INTEGER,
  "fg3a_rank" INTEGER,
  "fg3_pct_rank" INTEGER,
  "ftm_rank" INTEGER,
  "fta_rank" INTEGER,
  "ft_pct_rank" INTEGER,
  "oreb_rank" INTEGER,
  "dreb_rank" INTEGER,
  "reb_rank" INTEGER,
  "ast_rank" INTEGER,
  "tov_rank" INTEGER,
  "stl_rank" INTEGER,
  "blk_rank" INTEGER,
  "blka_rank" INTEGER,
  "pf_rank" INTEGER,
  "pfd_rank" INTEGER,
  "pts_rank" INTEGER,
  "plus_minus_rank" INTEGER,
  "nba_fantasy_pts_rank" INTEGER,
  "dd2_rank" INTEGER,
  "td3_rank" INTEGER,
  "wnba_fantasy_pts_rank" INTEGER,
  "available_flag" INTEGER,
  "min_sec" VARCHAR(30),
  "creation_timestamp" TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_player_id ON playerStatsPerGame(PLAYER_ID);
CREATE INDEX idx_player_id ON playerStatsPerGame(PLAYER_ID);
CREATE INDEX idx_player_id ON playerStatsPerGame(PLAYER_ID);
