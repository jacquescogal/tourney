// HomePage page should have:
import { Outlet, useNavigate } from "react-router-dom";
import SubHeader from "../../components/commons/SubHeader";
import { useEffect } from "react";
import Modal from "../../components/commons/Modal";
import TeamDetailPage from "../team_detail_page/TeamDetailPage";

const AdminPanel = (props:{modalOpen:boolean, setModalOpen:React.Dispatch<React.SetStateAction<boolean>>
  , teamID: number, setTeamID: React.Dispatch<React.SetStateAction<number>>
}) => {

  const nav = useNavigate();
  useEffect(() => {
    const userSession = sessionStorage.getItem("session");
    if (!userSession) {
      nav("/login");
    }else{
      nav("/admin/team");
    }
  }, []);

  
  return (
    <div className="bg-gt-white w-screen flex flex-col justify-center relative h-fit ">
      <SubHeader />
      <Modal isOpen={props.modalOpen} onClose={()=>{props.setModalOpen(false)}}>
        <TeamDetailPage team_id={props.teamID}/>
      </Modal>
      <div className="bg-blue-200 w-screen flex flex-row justify-center overflow-y-auto absolute top-0 top-sub-header">
        <Outlet />
      </div>
    </div>
  );
};

export default AdminPanel;
