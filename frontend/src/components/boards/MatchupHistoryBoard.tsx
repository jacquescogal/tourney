import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import {  ITeamMatchUpDetailRow } from "../../types/team";
import { GOTO_TEAM_DETAIL_PAGE } from "../../routes/team";
import { useNavigate } from "react-router-dom";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const MatchupHistoryBoard = (props:{matchupDetails: ITeamMatchUpDetailRow[]}) => {
  return (
    <div className="h-4/5 absolute bottom-0 w-full p-4">
      <div className="h-full w-full flex flex-col">
        <h1>Match History</h1>
        <BoardTeams {...props}/>
      </div>
    </div>
  );
};

const BoardTeams = (props:{matchupDetails: ITeamMatchUpDetailRow[]}) => {
  const nav = useNavigate();
  const rowData:ITeamMatchUpDetailRow[] = props.matchupDetails;

  // Column Definitions: Defines & controls grid columns.
  const colDefs: ColDef<ITeamMatchUpDetailRow>[] = [
    { headerName: "Match #", field: "match_id" },
    { headerName: "Round", field: "round_number" },
    { headerName: "Scored/Conceded", field: "goals_for_againt" },
    { field: "opponent" },
  ];

  const defaultColDef: ColDef = {
    flex: 1,
  };

  return (
    <div
      className={"ag-theme-quartz-dark"}
      style={{ width: "100%", height: "100%" }}
    >
      <AgGridReact
        rowData={rowData}
        columnDefs={colDefs}
        defaultColDef={defaultColDef}
        onRowClicked={(e) => {
          nav(GOTO_TEAM_DETAIL_PAGE(e.data.opponent_team_id));
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
  );
};

export default MatchupHistoryBoard;
