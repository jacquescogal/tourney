import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import axios from "axios";
import { useEffect, useState } from "react";
import {
  ITeamRanking,
  ITeamRankingRow,
} from "../../types/leaderboard";
import { parse } from "date-fns";
import MatchService from "../../api/MatchService";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const Leaderboard = () => {
  return (
    <div className="bg-gt-blue h-screen w-article-wide p-4">
      <div className="h-full w-full flex flex-col">
        <BoardRanking roundNumber={1} groupNumber={1} />
        <BoardRanking roundNumber={1} groupNumber={2} />
      </div>
    </div>
  );
};

const BoardRanking = (props: { roundNumber: number; groupNumber: number }) => {
  const [rowData, setRowData] = useState<ITeamRankingRow[]>([]);

  // Column Definitions: Defines & controls grid columns.
  const colDefs: ColDef<ITeamRankingRow>[] = ([
    { headerName: "Rank", field: "position" },
    { headerName: "Team", field: "team_name" },
    { headerName: "W/D/L", field: "wdl" },
    { headerName: "Total Goals", field: "goals" },
    {
      headerName: "Joined",
      field: "registration_date_ddmm",
      comparator: (valueA, valueB) => {
        const dateA = parse(valueA, "dd/MM", new Date());
        const dateB = parse(valueB, "dd/MM", new Date());
        console.log(dateA, dateB);
        if (dateA == dateB) return 0;
        return dateA > dateB ? 1 : -1;
      },
    },
  ]);

  const defaultColDef: ColDef = {
    flex: 1,
  };

  useEffect(() => {
    // Fetch match rankings from the API
    const fetchMatchRankings = async () => {
      try {
        const data = await MatchService.getMatchRankings({
          roundNumber: props.roundNumber,
          groupNumber: props.groupNumber
        })

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
        setRowData(teamRankingsRow);
      } catch (error) {
        // TODO: Handle error (e.g., network issues or invalid parameters)
        if (axios.isAxiosError(error)) {
          //   setError(error.response?.data.detail || "An error occurred");
        } else {
          //   setError("An unknown error occurred");
        }
      }
    };

    fetchMatchRankings();
  }, [props.groupNumber, props.roundNumber]);

  return (
    <div
      className={"ag-theme-quartz-dark"}
      style={{ width: "100%", height: "100%" }}
    >
      <AgGridReact
        rowData={rowData}
        columnDefs={colDefs}
        defaultColDef={defaultColDef}
        gridOptions={{
          rowClassRules:{
            'bg-green-600': (params) =>{return params.data.is_qualified === true}
          }
        }}
      />
    </div>
  );
};

export default Leaderboard;
