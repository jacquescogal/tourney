import React from 'react'
import CreateTeamForm from '../../components/forms/CreateTeamForm'
import Teamboard from '../../components/boards/Teamboard'


const CreateTeamPage = () => {
  return (
    <div className='flex flex-row'>
        <CreateTeamForm />
        <Teamboard />
    </div>
  )
}

export default CreateTeamPage