import { BatchRegisterTeamRequest } from '../types/team';
import { CREATE_TEAMS, GET_TEAM_BY_ID, GET_TEAMS } from '../api_routes/team';

class TeamService {
    public static fetchTeams = async (): Promise<Response> => {
      const response = await fetch(GET_TEAMS());
      return response;
      };

      public static fetchTeamDetailPage = async (team_id: number): Promise<Response> => {
        const response = await fetch(GET_TEAM_BY_ID(team_id));
        return response;
      };

      public static createTeams = async (payload: BatchRegisterTeamRequest): Promise<Response> => {
        const response = await fetch(CREATE_TEAMS(), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
        return response;
      };
  }

  

  

  


  
  
  export default TeamService;
