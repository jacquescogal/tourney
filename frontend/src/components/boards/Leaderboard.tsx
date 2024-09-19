import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { IMatchRankingResponse, ITeamRanking, ITeamRankingRow } from "../../types/leaderboard";
import { parse } from "date-fns";
import MatchService from "../../api/MatchService";
import { useNavigate } from "react-router-dom";
import { GOTO_TEAM_DETAIL_PAGE } from "../../routes/team";
import { WS_MATCHUP } from "../../api_routes/websocket";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const Leaderboard = () => {
  const [boardOneRowData, setBoardOneRowData] = useState<ITeamRankingRow[]>([]);
  const [boardTwoRowData, setBoardTwoRowData] = useState<ITeamRankingRow[]>([]);

  useEffect(() => {
    // Fetch match rankings from the API
    const fetchMatchRankings = async (params:{roundNumber:number, groupNumber:number, setRowData:React.Dispatch<React.SetStateAction<ITeamRankingRow[]>>} ) => {
      try {
        const response = await MatchService.getMatchRankings({
          roundNumber: params.roundNumber,
          groupNumber: params.groupNumber,
        });
        const data: IMatchRankingResponse = await response.json();

        // Check if the response contains the data and update the state
        const teamRankings: ITeamRanking[] =
          data.group_rankings[0].team_rankings;
        const teamRankingsRow: ITeamRankingRow[] = [];
        teamRankings.forEach((tr) => {
          const trr: ITeamRankingRow = {
            ...tr,
            wdl: `${tr.wins}/${tr.draws}/${tr.losses}`,
          };
          teamRankingsRow.push(trr);
        });
        params.setRowData(teamRankingsRow);
      } catch (error) {
        // TODO: Handle error (e.g., network issues or invalid parameters)
        if (axios.isAxiosError(error)) {
          //   setError(error.response?.data.detail || "An error occurred");
        } else {
          //   setError("An unknown error occurred");
        }
      }
    };

    fetchMatchRankings({roundNumber:1,groupNumber:1,setRowData:setBoardOneRowData});
    fetchMatchRankings({roundNumber:1,groupNumber:2,setRowData:setBoardTwoRowData});
  }, []);

  // websockets
  useEffect(() => {
    const connectWebSocket = () => {
      const socket = new WebSocket(WS_MATCHUP({roundNumber:1,groupNumber:1}));
      socket.onopen = () => {
        console.log('WebSocket connection opened');
      }
  
      socket.onmessage = (event) => {
        const data: IMatchRankingResponse = JSON.parse(event.data);  
        console.log('Received data:', data);
  
          const teamRankings: ITeamRanking[] =
            data.group_rankings[0].team_rankings;
          const teamRankingsRow: ITeamRankingRow[] = [];
          teamRankings.forEach((tr) => {
            const trr: ITeamRankingRow = {
              ...tr,
              wdl: `${tr.wins}/${tr.draws}/${tr.losses}`,
            };
            teamRankingsRow.push(trr);
          });
          setBoardOneRowData(teamRankingsRow);
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

  // websockets
  useEffect(() => {
    const connectWebSocket = () => {
    const socket = new WebSocket(WS_MATCHUP({roundNumber:1,groupNumber:2}));
    socket.onopen = () => {
      console.log('WebSocket connection opened');
    }

    socket.onmessage = (event) => {
      const data: IMatchRankingResponse = JSON.parse(event.data);  
      console.log('Received data:', data);

        const teamRankings: ITeamRanking[] =
          data.group_rankings[0].team_rankings;
        const teamRankingsRow: ITeamRankingRow[] = [];
        teamRankings.forEach((tr) => {
          const trr: ITeamRankingRow = {
            ...tr,
            wdl: `${tr.wins}/${tr.draws}/${tr.losses}`,
          };
          teamRankingsRow.push(trr);
        });
        setBoardTwoRowData(teamRankingsRow);
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
    <div className="h-screen-less-all-headers w-article-wide p-4">
      <div className="h-full w-full flex flex-col">
      <h1>Group {1}</h1>
        <BoardRanking rowData={boardOneRowData} />
        <h1>Group {2}</h1>
        <BoardRanking rowData={boardTwoRowData} />
      </div>
    </div>
  );
};

const BoardRanking = (props: { rowData:ITeamRankingRow[] }) => {
  const nav = useNavigate();

  // Column Definitions: Defines & controls grid columns.
  const colDefs: ColDef<ITeamRankingRow>[] = [
    { headerName: "Rank", field: "position", resizable: false , flex:1},
    { headerName: "Team", field: "team_name", flex: 2},
    { headerName: "W/D/L", field: "wdl" , flex: 1},
    { headerName: "Total Goals", field: "goals", flex:1},
    {
      headerName: "Joined",
      field: "registration_date_ddmm",
      comparator: (valueA, valueB) => {
        const dateA = parse(valueA, "dd/MM", new Date());
        const dateB = parse(valueB, "dd/MM", new Date());
        if (dateA == dateB) return 0;
        return dateA > dateB ? 1 : -1;
      },
      flex:2
    },
  ];

  const defaultColDef: ColDef = {
  };

  

  return (
    <>
      <div
        className={"ag-theme-quartz-dark"}
        style={{ width: "100%", height: "100%" }}
      >
        <AgGridReact
          rowData={props.rowData}
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
      </div>
    </>
  );
};

export default Leaderboard;
