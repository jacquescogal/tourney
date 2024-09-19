import { useLocation, useNavigate } from "react-router-dom"
import { IUserSession } from "../../types/session";
import { UserRole } from "../../types/user";

const Header = (props:{userSession:IUserSession | null, endSession:()=>void}) => {
    const nav = useNavigate()
    const location = useLocation();
    const currentPath = location.pathname;

  return (
    <div className='bg-gt-white h-header flex flex-row justify-between px-12 py-4'>
        {/* Header Banner */}
        <div className="text-center items-center content-center flex flex-row">
          <img src="/football-logo.png" className="h-header-1/2 object-scale-down cursor-pointer transition-all ease-in-out hover:scale-75"/>
          <span className="text-pop ml-2 bold select-none">Tournament Management System</span>
        </div>
        <div className="flex flex-row w-40 justify-between">
            {/* Links */}
            {props.userSession?.user_role ===UserRole.Enum.admin && <button className={`${currentPath.startsWith("/admin")?"underline":"hover:underline"}`} onClick={()=>{nav("/admin/team")}}>Dashboard</button>}
            {props.userSession && <button className={"hover:underline"} onClick={()=>{props.endSession();nav("/login")}}>Logout</button>}
        </div>
    </div>
  )
}

export default Header