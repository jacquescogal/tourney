import { useNavigate } from "react-router-dom"

const Header = () => {
    const nav = useNavigate()
  return (
    <div className='bg-test-green h-header'>
        {/* Header Banner */}
        <div>
            {/* Logo */}
        </div>
        <div>
            {/* Links */}
            <button onClick={()=>{nav("/")}}>home</button>

            <button onClick={()=>{nav("/login")}}>login</button>
        </div>
    </div>
  )
}

export default Header