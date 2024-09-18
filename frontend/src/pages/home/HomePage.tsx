// HomePage page should have:
import { Outlet } from "react-router-dom";
import Leaderboard from "../../components/boards/Leaderboard";
import Teamboard from "../../components/boards/Teamboard";
import CreateTeamForm from "../../components/forms/CreateTeamForm";
import SubHeader from "../../components/commons/SubHeader";

const HomePage = () => {
  return (
    <div className="bg-gt-white w-screen flex flex-col justify-center ">
      <SubHeader/>
      <div className="bg-blue-200 w-screen flex flex-row justify-center ">
        <Outlet />
      </div>
    </div>
  );
};

export default HomePage;
