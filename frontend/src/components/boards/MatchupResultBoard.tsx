import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import {
  ITeamMatchResultRow,
  ITeamMatchResultRowHolder,
} from "../../types/team";
// import { useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";
import MatchService from "../../api/MatchService";
import axios from "axios";
import { WS_MATCHRESULTS, WS_MATCHUP } from "../../api_routes/websocket";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const MatchupResultBoard = (props:{leaderBoardToggle?:React.ReactNode}) => {
  return (
    <div className="h-screen-less-all-headers w-article-wide p-4">
      <div className="h-full w-full flex flex-col relative">
      <div className="flex flex-row items-center">
      <h1 className="h-[30px] underline text-2xl">Match History</h1>
      {props.leaderBoardToggle}
      </div>
        <BoardTeams />
      </div>
    </div>
  );
};

const BoardTeams = () => {
  //   const nav = useNavigate();
  const [rowData, setRowData] = useState<ITeamMatchResultRow[]>([]);

  const DeleteButton = (props: { value: number }) => {
    return (
      <div className="h-full w-full flex items-center justify-around content-center">
        <div
          className="h-3/4 w-3/4 bg-red-500 rounded text-center items-center justify-center mx-2 flex cursor-pointer"
          onClick={() => {
            console.log(props.value);
            //   deleteTeam(props.value);
          }}
        >
          Del
        </div>
      </div>
    );
  };

  // Column Definitions: Defines & controls grid columns.
  const colDefs: ColDef<ITeamMatchResultRow>[] = [
    { headerName: "Match #", field: "match_id" },
    { headerName: "Round", field: "round_number" },
    {
      headerName: "Goals",
      field: "team_1_goals",
      editable: true,
      cellClass: () => {
        return `bg-slate-700 outline outline-blue-200 text-orange-300`;
      },
},
    {
      headerName: "Match Up",
      valueGetter: (params) => {
        return `${params.data?.team_1_name} vs ${params.data?.team_2_name}`;
      },
    },
    { headerName: "Goals", field: "team_2_goals", editable: true,
        cellClass: () => {
          return `bg-slate-700 outline outline-blue-200 text-orange-300`;
        },},
    {
      headerName: "Options",
      cellRenderer: DeleteButton,
      valueGetter: (params) => {
        return params.data?.match_id;
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
        const response = await MatchService.getMatchResults({
          roundNumber: 1
        });
        const data: ITeamMatchResultRowHolder = await response.json();
        setRowData(data.match_results);
      } catch (error) {
        if (axios.isAxiosError(error)) {
          //   setError(error.response?.data.detail || "An error occurred");
        } else {
          //   setError("An unknown error occurred");
        }
      }
    };

    fetchTeams();
  }, []);

  // websockets
  useEffect(() => {
    const connectWebSocket = () => {
    const socket = new WebSocket(WS_MATCHRESULTS({roundNumber:1}));
    socket.onopen = () => {
      console.log('WebSocket connection opened');
    }

    socket.onmessage = (event) => {
      const data: ITeamMatchResultRowHolder = JSON.parse(event.data);  
      setRowData(data.match_results);
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

  return (
    <>
    
    <div
        className={"ag-theme-quartz-dark absolute bottom-0 h-[calc(100%-50px)]"}
        style={{ width: "100%" }}
      >
      <AgGridReact
        rowData={rowData}
        columnDefs={colDefs}
        defaultColDef={defaultColDef}
        // onRowClicked={(e) => {
        //   nav(GOTO_TEAM_DETAIL_PAGE(e.data.opponent_team_id));
        // }}
        gridOptions={
          {
              rowClassRules: {
                "bg-green-600": (params) => {
                  return params.node.isSelected()===true;
                },
              },
          }
        }
      />
    </div>
    </>
  );
};

export default MatchupResultBoard;
