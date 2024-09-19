// HomePage page should have:
import { Outlet, useNavigate } from "react-router-dom";
import SubHeader from "../../components/commons/SubHeader";
import { useEffect } from "react";

const AdminPanel = () => {
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
    <div className="bg-gt-white w-screen flex flex-col justify-center ">
      <SubHeader />
      <div className="bg-blue-200 w-screen flex flex-row justify-center ">
        <Outlet />
      </div>
    </div>
  );
};

export default AdminPanel;
