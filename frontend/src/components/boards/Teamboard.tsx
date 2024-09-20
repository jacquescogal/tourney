import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ColDef, ModuleRegistry } from "@ag-grid-community/core";
import { AgGridReact } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { parse } from "date-fns";
import { ITeam, UpdateTeamRequestSchema } from "../../types/team";
import TeamService from "../../api/TeamService";
import { WS_TEAMS } from "../../api_routes/websocket";
ModuleRegistry.registerModules([ClientSideRowModelModule]);

const Teamboard = (props: { appendToConsole: (text: string) => void ,setModalOpen: React.Dispatch<React.SetStateAction<boolean>>,setTeamID:React.Dispatch<React.SetStateAction<number>>}) => {
  return (
    <div className="h-screen-less-all-headers w-article-wide p-4">
      <div className="h-full w-full flex flex-col relative">
        <BoardTeams {...props} />
      </div>
    </div>
  );
};

const BoardTeams = (prop: { appendToConsole: (text: string) => void ,setModalOpen: React.Dispatch<React.SetStateAction<boolean>>,setTeamID:React.Dispatch<React.SetStateAction<number>>}) => {
  const [rowData, setRowData] = useState<ITeam[]>([]);
  const deleteTeam = async (team_id: number) => {
    try {
      const response = await TeamService.deleteTeam(team_id);
      if (response.ok) {
        prop.appendToConsole(
          `Delete team_id:\n${team_id}\nServer Response:\nsuccess`
        );
      }
    } catch (error) {
      prop.appendToConsole(
        `Delete team_id:\n${team_id}\nServer Response:\n${error}`
      );
    }
  };

  const ButtonGroup = (props: { value: number }) => {
    return (
      <div className="h-full w-full flex items-center justify-around content-center">
        <div
          className="h-3/4 w-3/4 bg-blue-500 rounded text-center items-center justify-center mx-2 flex cursor-pointer"
          onClick={() => {
            prop.setTeamID(props.value);
            prop.setModalOpen(true);
          }}
        >
          View
        </div>
        <div
          className="h-3/4 w-3/4 bg-red-500 rounded text-center items-center justify-center mx-2 flex cursor-pointer"
          onClick={() => {
            console.log(props.value);
            deleteTeam(props.value);
          }}
        >
          Del
        </div>
      </div>
    );
  };

  const colDefs: ColDef<ITeam>[] = [
    { headerName: "Group", field: "group_number" },
    { headerName: "Team", field: "team_name", editable: true,cellClass: () => {
      return `bg-slate-700 outline outline-blue-200 text-orange-300`;
    },},
    {
      headerName: "Joined",
      field: "registration_date_ddmm",
      comparator: (valueA, valueB) => {
        const dateA = parse(valueA, "dd/MM", new Date());
        const dateB = parse(valueB, "dd/MM", new Date());
        if (dateA == dateB) return 0;
        return dateA > dateB ? 1 : -1;
      },
      editable: true,
      cellClass: () => {
        return `bg-slate-700 outline outline-blue-200 text-orange-300`;
      },
    },
    {
      headerName: "Options",
      cellRenderer: ButtonGroup,
      valueGetter: (params) => {
        return params.data?.team_id;
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
    <h1 className="h-[30px] underline text-2xl">Teams</h1>
      <div
        className={"ag-theme-quartz-dark absolute bottom-0 h-[calc(100%-40px)]"}
        style={{ width: "100%" }}
      >
        <AgGridReact
          rowData={rowData}
          columnDefs={colDefs}
          defaultColDef={defaultColDef}
          onCellEditingStopped={(e) => {
            if (e.column.getColId() === "registration_date_ddmm") {
              const isValid =
                UpdateTeamRequestSchema.shape.registration_date_ddmm.safeParse(
                  e.newValue
                );
              if (isValid.success) {
                // update the value
                const updateDate = async () => {
                  try {
                    TeamService.updateTeam(e.node.data.team_id, {
                      team_name: e.node.data.team_name,
                      registration_date_ddmm: e.newValue,
                    });
                  } catch (error) {
                    console.log(error);
                  }
                };
                updateDate();
              } else {
                // undo the change
                e.node.setDataValue(e.column.getColId(), e.oldValue);
              }
            } else if (e.column.getColId() === "team_name") {
              const isValid = UpdateTeamRequestSchema.shape.team_name.safeParse(
                e.value
              );
              if (isValid.success) {
                // update the value
                TeamService.updateTeam(e.node.data.team_id, {
                  team_name: e.newValue,
                  registration_date_ddmm: e.node.data.registration_date_ddmm,
                });
              } else {
                // undo the change
                e.node.setDataValue(e.column.getColId(), e.oldValue);
              }
            }
          }}
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
