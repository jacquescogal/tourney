import React from "react";
import Button from "../../components/commons/Button";
import { UserLoginRequest, UserLoginRequestSchema } from "../../types/user";
import SessionService from "../../api/SessionService";
import { useNavigate } from "react-router-dom";
import { IUserSession } from "../../types/session";

const LoginPage = (props:{setUserSession:React.Dispatch<React.SetStateAction<IUserSession | null>>}) => {
  return (
    <div className="bg-gt-blue h-screen-less-header flex flex-row items-center justify-evenly">
      <TextField />
      <LoginForm {...props}/>
    </div>
  );
};

const TextField = () => {
  return (
    <div className="text-white h-96  w-[30rem]">
      <h1 className="text-3xl">Tournament Management System</h1>
      <body className="text-lg mt-4">Welcome to the demo.</body>
      <p className="text-lg mt-4">
        <span className="text-orange-300">Continue as guest</span> to view live
        tournament results{" "}
      </p>
      <p className="text-lg my-4">
        <span className="text-orange-300">Login as admin</span> for all
        privilegese including editing team and match details
      </p>
      <p className="text-lg my-4">
        <span className="text-orange-300">Login as team manager</span> to
        register players and edit team information
      </p>
      <p className="text-lg mt-4">
        <span className="text-orange-300">Login as player</span> to edit your
        own information
      </p>
    </div>
  );
};

const LoginForm = (props:{setUserSession:React.Dispatch<React.SetStateAction<IUserSession | null>>}) => {
    const nav = useNavigate();
    const [username, setUsername] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [passwordError, setPasswordError] = React.useState(false);
    const [usernameError, setUsernameError] = React.useState(false)
    const [error, setError] = React.useState('');

    const submitLogin = async (e:React.MouseEvent<HTMLElement>)=>{
        e.preventDefault();
        const userLoginRequest: UserLoginRequest = {
            username: username,
            password: password
        }
        const userNameValidationResult = UserLoginRequestSchema.shape.username.safeParse(userLoginRequest.username);
        const passwordValidationResult = UserLoginRequestSchema.shape.password.safeParse(userLoginRequest.password);
        setUsernameError(!userNameValidationResult.success);
        setPasswordError(!passwordValidationResult.success);
        if(!userNameValidationResult.success){
            setError(userNameValidationResult.error.errors[0].message);
            return;
        }else if(!passwordValidationResult.success){
            setError(passwordValidationResult.error.errors[0].message);
            return;
        }else{
            setError('');
        }
        try{
            const response = await SessionService.createSession(userLoginRequest);
            if(response.status === 200){
                const data = await response.json();
                props.setUserSession(data);
                sessionStorage.setItem('session', JSON.stringify(data));
                nav('/admin/team');
            }
            else{
                const data = await response.json();
                setError(data.detail);
            }
        }
        catch (e){
            console.error(e);
            setError('Invalid username or password');
        }
    }

  return (
    <div className="relative h-96 w-80">
      <div className="absolute h-full w-full flex flex-col justify-center items-center content-center z-10 ">
        {/* form to login with dropdown for roles */}
        <form className="flex flex-col gap-4">
          <input
          value={username}
            onChange={(e)=>{setUsername(e.target.value); setUsernameError(false)}}
            type="text"
            placeholder="Username"
            className={`border border-gray-300 rounded p-2 ${usernameError ? 'border-red-500' : ''}`}
          />
          <input
            value={password}
            onChange={(e)=>{setPassword(e.target.value); setPasswordError(false)}}
            type="password"
            placeholder="Password"
            className={`border border-gray-300 rounded p-2 ${passwordError ? 'border-red-500' : ''}`}
          />
          <Button className="w-full bg-blue-400 text-black" onClick={submitLogin}>Login</Button>
          <Button className="w-full text-white bg-orange-400 hover:bg-orange-600">Continue as Guest</Button>
        </form>

        <span className="text-red-500 h-2 m-2 text-sm">{error}</span>
      </div>
      <div className="absolute top-0 left-0 z-0 h-full w-full bg-white bg-opacity-90 rounded shadow backdrop-blur-md border"></div>
    </div>
  );
};

export default LoginPage;
