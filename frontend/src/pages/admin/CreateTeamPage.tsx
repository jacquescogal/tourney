import React, { useState } from 'react'
import CreateTeamForm from '../../components/forms/CreateTeamForm'
import Teamboard from '../../components/boards/Teamboard'


const CreateTeamPage = (props:{setModalOpen: React.Dispatch<React.SetStateAction<boolean>>,setTeamID:React.Dispatch<React.SetStateAction<number>>}) => {
  const [consoleText, setConsoleText] = useState<string>("");
  const appendToConsole = (text: string) => {
    setConsoleText(consoleText + text + "\n---\n");
  };
  
  return (
    <div className='flex flex-row'>
        <CreateTeamForm consoleText={consoleText} appendToConsole={appendToConsole}
        content={<div className=" h-96  w-article-wide text-gt-blue outline rounded my-2 bg-white shadow-inner p-2">
          <h1 className="text-3xl">Manage Teams Here (Round 1)</h1>
          <p className="text-lg mt-1">1. Create Teams in form below</p>
          <p className="text-lg mt-1">2. Edit Outlined Cells on right</p>
          <p className="text-lg mt-1">3. Delete Teams on right (will delete associated matches)</p>
        </div>}/>
        <Teamboard appendToConsole={appendToConsole} setModalOpen={props.setModalOpen} setTeamID={props.setTeamID}/>
        
    </div>
  )
}

export default CreateTeamPage