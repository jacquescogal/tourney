import React, { useState } from 'react'
import CreateTeamForm from '../../components/forms/CreateTeamForm'
import Teamboard from '../../components/boards/Teamboard'
import TeamService from '../../api/teamService'


const CreateTeamPage = () => {
  const [consoleText, setConsoleText] = useState<string>("");
  const appendToConsole = (text: string) => {
    setConsoleText(consoleText + text + "\n---\n");
  };
  
  return (
    <div className='flex flex-row'>
        <CreateTeamForm consoleText={consoleText} appendToConsole={appendToConsole}/>
        <Teamboard appendToConsole={appendToConsole}/>
    </div>
  )
}

export default CreateTeamPage