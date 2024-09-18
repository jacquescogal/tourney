import axios from 'axios';
import { ITeam, ITeamDetails } from '../types/team';
import { GET_TEAM_BY_ID, GET_TEAMS } from '../api_routes/team';


class TeamService {
    public static fetchTeams = async (): Promise<ITeam[]> => {
        const response = await axios.get<ITeam[]>(GET_TEAMS());
        return response.data;
      };

      public static fetchTeamDetailPage = async (team_id: number): Promise<ITeamDetails> => {
        const response = await axios.get<ITeamDetails>(GET_TEAM_BY_ID(team_id));
        return response.data;
      };
  }
  
  export default TeamService;
