//InitBallot views should only last for 1 month maximum. Anything in the database for longer than that is a glitch. This is a failsafe that deletes them.

use rusqlite::{params, Connection, Result};
use dotenv::dotenv;
use std::time::{SystemTime, UNIX_EPOCH};

use std::env;

fn main() -> Result<()> {
    //get database
    dotenv().ok();
    let databasePath = env::var("BOT_DATABASE_PATH").unwrap();
    let conn = Connection::open(&databasePath)?;
    let glitchConn = Connection::open(&databasePath)?;
    let mut table = conn.prepare("SELECT * FROM InitBallots")?;
    glitchConn.execute("CREATE TABLE IF NOT EXISTS GlitchedViews (newID INTEGER PRIMARY KEY, id INTEGER, messageID INTEGER NOT NULL, channelID INTEGER NOT NULL, electionID TEXT NOT NULL, time INTEGER NOT NULL, timeDeleted INTEGER NOT NULL)", []);

    //change database into usable data
    let rows = table.query_map([], |row| {
        let id: i32 = row.get(0)?;
        let messageID: i64 = row.get(1)?;
        let channelID: i64 = row.get(2)?;
        let electionID: String = row.get(3)?;
        let time: i64 = row.get(4)?;
        
        Ok((id, messageID, channelID, electionID, time))
    })?;

    //delete rows that have existed longer than a month and a day
    let prepNow = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    let now: i64 = prepNow.as_secs().try_into().unwrap();
    for r in rows{
        let (id, messageID, channelID, electionID, time) = r?;
        if (time + 2716143) < now{
            conn.execute("DELETE FROM InitBallots WHERE id = ?", params![id]);
            conn.execute("INSERT INTO GlitchedViews (id, messageID, channelID, electionID, time, timeDeleted) VALUES (?, ?, ?, ?, ?, ?)", params![id, messageID, channelID, electionID, time, now]);
            println!("Found glitched view. Please review the GlitchedViews table \n id : {}, messageID: {}, channelID: {}, election ID: {}, time: {}", id, messageID, channelID, electionID, time);
        }
    }
    println!("All glitched views removed from database, if any");
    Ok(())
}