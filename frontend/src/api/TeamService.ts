import axios from 'axios';
import { ITeam } from '../types/team';
import { GET_TEAMS } from '../api-routes/team';


class TeamService {
    public static fetchTeams = async (): Promise<ITeam[]> => {
        const response = await axios.get<ITeam[]>(GET_TEAMS());
        return response.data;
      };
  }
  
  export default TeamService;