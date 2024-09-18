import React from 'react'
import Leaderboard from '../../components/boards/Leaderboard'
import CreateMatchResultForm from '../../components/forms/CreateMatchResultForm'


const CreateMatchupPage = () => {
  return (
    <div className='flex flex-row'>
        <CreateMatchResultForm/>
        <Leaderboard />
    </div>
  )
}

export default CreateMatchupPage