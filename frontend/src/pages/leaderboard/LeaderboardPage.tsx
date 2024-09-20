import React from 'react'
import Leaderboard from '../../components/boards/Leaderboard'
import TeamDetailPage from '../team_detail_page/TeamDetailPage'
import Modal from '../../components/commons/Modal'

const LeaderboardPage = (props:{modalOpen:boolean, setModalOpen:React.Dispatch<React.SetStateAction<boolean>>
    , teamID: number, setTeamID: React.Dispatch<React.SetStateAction<number>>
  }) => {
  return (
    <div className='w-full h-screen-less-header bg-gt-off-white flex justify-center justify-center items-center '>
        <Modal isOpen={props.modalOpen} onClose={()=>{props.setModalOpen(false)}}>
        <TeamDetailPage team_id={props.teamID}/>
      </Modal>
        <div className="text-white h-96  w-[30rem] bg-gt-blue h-fit rounded p-4">
      <h1 className="text-3xl">Tournament Management System</h1>
      <body className="text-lg mt-4">Welcome to the demo.</body>
      <p className="text-lg mt-4">
        <span className="text-orange-300">Current Round:</span> 1{" "}
      </p>
    </div>

        <Leaderboard  {...props}/>
    </div>
  )
}

export default LeaderboardPage