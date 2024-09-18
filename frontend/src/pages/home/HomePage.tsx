
// HomePage page should have:

import Leaderboard from "../../components/boards/Leaderboard";
import Teamboard from "../../components/boards/Teamboard";

// 1 LeaderBoard
const HomePage = () => {
  return (
    <div className='bg-gt-white h-screen w-screen bg-red-200 flex justify-center '>
      <Leaderboard/>
      <Teamboard/>
    </div>
  )
}

export default HomePage;