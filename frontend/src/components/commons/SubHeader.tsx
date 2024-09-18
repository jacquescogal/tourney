import { useLocation, useNavigate } from "react-router-dom"

const SubHeader = () => {
    const nav = useNavigate()
    const location = useLocation();
    const currentPath = location.pathname;
  return (
        <div className="bg-gt-blue h-sub-header flex flex-row justify-center items-center text-white select-none">
        <span onClick={()=>{nav("team")}} className=
        {`${currentPath.endsWith("team")?"brightness-125":""} bg-gt-blue w-32 text-center hover:shadow-inner hover:brightness-125 h-full content-center px-4 cursor-pointer`}>
        Team
        </span>
        <span onClick={()=>{nav("matchup")}} className=
        {`${currentPath.endsWith("matchup")?"brightness-125":""} bg-gt-blue w-32 text-center hover:shadow-inner hover:brightness-125 h-full content-center px-4 cursor-pointer`}>
        Match up
        </span>
        </div>
  )
}

export default SubHeader