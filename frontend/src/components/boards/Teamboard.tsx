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

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const Teamboard = () => {
  return (
    <div className="bg-gt-blue h-screen w-article-wide-1/2 p-4">
      <div className="h-full w-full flex flex-col">
        <BoardTeams />
      </div>
    </div>
  );
};

const BoardTeams = () => {
  const [rowData, setRowData] = useState<ITeam[]>([]);

  // Column Definitions: Defines & controls grid columns.
  const colDefs: ColDef<ITeam>[] = ([
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
  ]);

  const defaultColDef: ColDef = {
    flex: 1,
  };

  useEffect(() => {
    // Fetch all teams from the API
    const fetchTeams = async () => {
      try {
        const data = await TeamService.fetchTeams();
        console.log(data)
        setRowData(data);
      } catch (error) {
        console.log(error)
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

export default Teamboard;
