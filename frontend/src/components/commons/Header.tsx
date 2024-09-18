import { useNavigate } from "react-router-dom"

const Header = () => {
    const nav = useNavigate()
  return (
    <div className='bg-test-green h-20'>
        {/* Header Banner */}
        <div>
            {/* Logo */}
        </div>
        <div>
            {/* Links */}
            <button onClick={()=>{nav("/create_team")}}>Hello</button>
        </div>
    </div>
  )
}

export default Header