import React from "react";

const Button = (props: { className?: string, children: React.ReactNode, onClick?: (e:React.MouseEvent<HTMLElement>)=>void }) => {
  return (
    <button
      className={`${props.className} shadow-xl outline-offset-0 
outline-2 bg-gt-white outline-gt-blue shadow w-fit p-2 rounded transition-all ease-out duration-50 hover:bg-gt-blue hover:text-white hover:outline-1 m-1`}
      type="submit"
      onClick={props.onClick}
    >
      {props.children}
    </button>
  );
};

export default Button;
