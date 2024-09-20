import { BatchRegisterTeamRequest, UpdateTeamRequest } from "../types/team";
import { CREATE_TEAMS, DELETE_TEAM_BY_ID, GET_TEAM_BY_ID, GET_TEAMS, PUT_TEAM_BY_ID } from "../api_routes/team";

class TeamService {
  public static fetchTeams = async (): Promise<Response> => {
    const response = await fetch(GET_TEAMS());
    return response;
  };

  public static fetchTeamDetailPage = async (
    team_id: number
  ): Promise<Response> => {
    const response = await fetch(GET_TEAM_BY_ID(team_id));
    return response;
  };

  public static createTeams = async (
    payload: BatchRegisterTeamRequest
  ): Promise<Response> => {
    const response = await fetch(CREATE_TEAMS(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return response;
  };

  public static updateTeam = async (
    team_id: number,
    payload: UpdateTeamRequest
  ): Promise<Response> => {
    const response = await fetch(PUT_TEAM_BY_ID(team_id), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return response;
  }

  public static deleteTeam = async (team_id: number): Promise<Response> => {
    const response = await fetch(DELETE_TEAM_BY_ID(team_id), {
      method: "DELETE",
      credentials: "include",
    });
    return response;
  };
}
export default TeamService;
