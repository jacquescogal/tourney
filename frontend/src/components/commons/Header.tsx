import { useLocation, useNavigate } from "react-router-dom"

const Header = () => {
    const nav = useNavigate()
    const location = useLocation();
    const currentPath = location.pathname;
  return (
    <div className='bg-gt-off-white h-header flex flex-row justify-between px-12 py-4'>
        {/* Header Banner */}
        <div className="text-center items-center content-center flex flex-row">
          <img src="/football-logo.png" className="h-header-1/2 object-scale-down cursor-pointer transition-all ease-in-out hover:scale-75"/>
          <span className="text-pop ml-2 bold select-none">Tournament Management System</span>
        </div>
        <div className="flex flex-row w-40 justify-between">
            {/* Links */}
            <button className={`${currentPath.endsWith("/admin")?"underline":""}`} onClick={()=>{nav("/admin")}}>Dashboard</button>
            <button className={`${currentPath.endsWith("/login")?"underline":""}`} onClick={()=>{nav("/login")}}>Login</button>
        </div>
    </div>
  )
}

export default Header