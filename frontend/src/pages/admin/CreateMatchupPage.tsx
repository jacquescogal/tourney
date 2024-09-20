import React, { useState } from 'react'
import Leaderboard from '../../components/boards/Leaderboard'
import CreateMatchResultForm from '../../components/forms/CreateMatchResultForm'
import MatchupResultBoard from '../../components/boards/MatchupResultBoard'
import Button from '../../components/commons/Button'


const CreateMatchupPage = (props:{setModalOpen: React.Dispatch<React.SetStateAction<boolean>>,setTeamID:React.Dispatch<React.SetStateAction<number>>}) => {
  const [leaderBoardToggle,setLeaderBoardToggle] = React.useState<boolean>(false);
  const [consoleText, setConsoleText] = useState<string>("");
  const appendToConsole = (text: string) => {
    setConsoleText(consoleText + text + "\n---\n");
  };
  const leaderBoardButtonToggle = <Button  onClick={()=>setLeaderBoardToggle(!leaderBoardToggle)}>{leaderBoardToggle ? "Show Matchup History" : "Show Leaderboard"}</Button>
  return (
    <div className='flex flex-row'>
        <CreateMatchResultForm consoleText={consoleText} appendToConsole={appendToConsole}
        content={<div className=" h-96  w-article-wide text-gt-blue outline rounded my-2 bg-white shadow-inner p-2">
          <h1 className="text-3xl">Manage Match Results Here (Round 1)</h1>
          <p className="text-lg mt-1">1. Create Match Results in form below</p>
          <p className="text-lg mt-1">2. Edit Outlined Cells on right</p>
          <p className="text-lg mt-1">3. Delete Matches on right</p>

      
        </div>}/>
        {
          leaderBoardToggle ? <Leaderboard  leaderBoardToggle={leaderBoardButtonToggle} {...props}/> : <MatchupResultBoard 
          leaderBoardToggle={leaderBoardButtonToggle}/>
        }
    </div>
  )
}

export default CreateMatchupPage