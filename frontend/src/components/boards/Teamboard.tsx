import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { parse } from "date-fns";
import { ITeam } from "../../types/team";
import TeamService from "../../api/teamService";
import { GOTO_TEAM_DETAIL_PAGE } from "../../routes/team";
import { useNavigate } from "react-router-dom";
import { WS_TEAMS } from "../../api_routes/websocket";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const Teamboard = () => {
  return (
    <div className="h-screen-less-all-headers w-article-wide p-4">
      <div className="h-full w-full flex flex-col relative">
        <BoardTeams />
      </div>
    </div>
  );
};

const BoardTeams = () => {
  const nav = useNavigate();
  const [rowData, setRowData] = useState<ITeam[]>([]);

  // Column Definitions: Defines & controls grid columns.
  const colDefs: ColDef<ITeam>[] = [
    { headerName: "Group", field: "group_number" },
    { headerName: "Team", field: "team_name" },
    {
      headerName: "Joined",
      field: "registration_date_ddmm",
      comparator: (valueA, valueB) => {
        const dateA = parse(valueA, "dd/MM", new Date());
        const dateB = parse(valueB, "dd/MM", new Date());
        if (dateA == dateB) return 0;
        return dateA > dateB ? 1 : -1;
      },
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
        console.log('WebSocket connection opened');
      }
  
      socket.onmessage = (event) => {
        const data:  ITeam[] = JSON.parse(event.data);  
        console.log('Received data:', data);
        setRowData(data);
      };
  
  
      socket.onclose = () => {
        console.log('WebSocket connection closed');
        setTimeout(connectWebSocket, 5000);
      };
  
      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      return () => {
        console.log('Closing WebSocket connection');
        socket.close();
      };
    }
    connectWebSocket();
  }, []); 

  return (<>
      <h1 className="h-[25px]">Teams</h1>
    <div
      className={"ag-theme-quartz-dark absolute bottom-0 h-[calc(100%-25px)]"}
      style={{ width: "100%" }}
    >
      <AgGridReact
        rowData={rowData}
        columnDefs={colDefs}
        defaultColDef={defaultColDef}
        onRowClicked={(e) => {
          nav(GOTO_TEAM_DETAIL_PAGE(e.data.team_id));
        }}
        gridOptions={{
          rowClass: "cursor-pointer",
          rowClassRules: {
            "bg-green-600": (params) => {
              return params.data.is_qualified === true;
            },
          },
        }}
      />
    </div></>
  );
};

export default Teamboard;
