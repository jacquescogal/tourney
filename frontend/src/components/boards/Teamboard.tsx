import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import axios from "axios";
import { useEffect, useRef, useState } from "react";
import { parse } from "date-fns";
import { ITeam } from "../../types/team";
import TeamService from "../../api/teamService";
// import { GOTO_TEAM_DETAIL_PAGE } from "../../routes/team";
// import { useNavigate } from "react-router-dom";
import { WS_TEAMS } from "../../api_routes/websocket";
import Button from "../commons/Button";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const Teamboard = (props:{appendToConsole:(text: string) => void}) => {
  return (
    <div className="h-screen-less-all-headers w-article-wide p-4">
      <div className="h-full w-full flex flex-col relative">
        <BoardTeams {...props}/>
      </div>
    </div>
  );
};

const BoardTeams = (props:{appendToConsole:(text: string) => void}) => {
  // const nav = useNavigate();
  const oldCellValue = useRef<string | null>(null);
  const [rowData, setRowData] = useState<ITeam[]>([]);
  const deleteTeam = async (team_id: number) => {
    try {
      const response = await TeamService.deleteTeam(team_id);
      if (response.ok) {
        props.appendToConsole(`Delete team_id:\n${team_id}\nServer Response:\nsuccess`);
      }
    } catch (error) {
      props.appendToConsole(`Delete team_id:\n${team_id}\nServer Response:\n${error}`);
    }
  }

  
  const ButtonGroup = (props:{value:number }) => {
    return (
      <div className="h-full w-full flex items-center justify-around content-center">
        <div className="h-3/4 w-3/4 bg-green-400 rounded text-center items-center justify-center mx-2 flex cursor-pointer">Edit</div>
        <div className="h-3/4 w-3/4 bg-red-500 rounded text-center items-center justify-center mx-2 flex cursor-pointer"
        onClick={()=>{
          console.log(props.value);
          deleteTeam(props.value);
        }}>Del</div>
      </div>
    );
  };

  const colDefs: ColDef<ITeam>[] = [
    { headerName: "Group", field: "group_number" },
    { headerName: "Team", field: "team_name" , editable:true},
    {
      headerName: "Joined",
      field: "registration_date_ddmm",
      comparator: (valueA, valueB) => {
        const dateA = parse(valueA, "dd/MM", new Date());
        const dateB = parse(valueB, "dd/MM", new Date());
        if (dateA == dateB) return 0;
        return dateA > dateB ? 1 : -1;
      },
      editable:true
    },
    {
      headerName: "Options",
      cellRenderer: ButtonGroup,
      valueGetter: (params) => {
        return params.data?.team_id;
      }
    },
  ];

  const defaultColDef: ColDef = {
    flex: 1,
  };

  useEffect(() => {
    // Fetch all teams from the API
    const fetchTeams = async () => {
      try {
        const response = await TeamService.fetchTeams();
        const data: ITeam[] = await response.json();
        setRowData(data);
      } catch (error) {
        console.log(error);
        // TODO: Handle error (e.g., network issues or invalid parameters)
        if (axios.isAxiosError(error)) {
          //   setError(error.response?.data.detail || "An error occurred");
        } else {
          //   setError("An unknown error occurred");
        }
      }
    };

    fetchTeams();
  }, []);

  useEffect(() => {
    const connectWebSocket = () => {
      const socket = new WebSocket(WS_TEAMS());
      socket.onopen = () => {
        console.log("WebSocket connection opened");
      };

      socket.onmessage = (event) => {
        const data: ITeam[] = JSON.parse(event.data);
        console.log("Received data:", data);
        setRowData(data);
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed");
        setTimeout(connectWebSocket, 5000);
      };

      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
      return () => {
        console.log("Closing WebSocket connection");
        socket.close();
      };
    };
    connectWebSocket();
  }, []);

  return (
    <>
      <h1 className="h-[25px]">Teams</h1>
      <div
        className={"ag-theme-quartz-dark absolute bottom-0 h-[calc(100%-25px)]"}
        style={{ width: "100%" }}
      >
        <AgGridReact
          rowData={rowData}
          columnDefs={colDefs}
          defaultColDef={defaultColDef}
          onCellEditingStopped={(e) => {
            console.log(e.column.getColId());
            console.log(e.oldValue);
            console.log(e.newValue);  
          }}
          // onCellE
          // onCellEditingStopped={(e) => {
          //   console.log(e.data);
          // }}
          onRowClicked={(e) => {
            console.log(e.data.team_id);
          }}
          gridOptions={{
            rowClassRules: {
              "bg-green-600": (params) => {
                return params.data.is_qualified === true;
              },
            },
          }}
        />
      </div>
    </>
  );
};

export default Teamboard;
