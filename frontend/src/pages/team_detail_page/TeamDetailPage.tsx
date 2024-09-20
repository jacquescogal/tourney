import { useEffect, useState } from "react";
import axios from "axios";
import { ITeamDetails, ITeamMatchUpDetail, ITeamMatchUpDetailRow } from "../../types/team";
import TeamService from "../../api/TeamService";
import MatchupHistoryBoard from "../../components/boards/MatchupHistoryBoard";

const TeamDetailPage = (props:{team_id?:number}) => {
  const {team_id} = props;
  const [teamDetails, setTeamDetails] = useState<ITeamDetails | null>(null);
  const [matchupDetailRows, setMatchupDetailRows] = useState<ITeamMatchUpDetailRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch team data from the API
  useEffect(() => {
    const fetchTeamDetails = async (team_id:number) => {
      try {
        const response = await TeamService.fetchTeamDetailPage(team_id);
        const data:ITeamDetails = await response.json();
        const rawMatchupDetails: ITeamMatchUpDetail[] = data.match_ups;
        const parsedMatchupDetailsRows: ITeamMatchUpDetailRow[] = [];
        rawMatchupDetails.forEach((md:ITeamMatchUpDetail) => {
          const parsedMD: ITeamMatchUpDetailRow = {
            ...md,
            goals_for_againt: `${md.goals_scored}/${md.goals_conceded}`
          }
          parsedMatchupDetailsRows.push(parsedMD)
        })
        setMatchupDetailRows(parsedMatchupDetailsRows)
        setTeamDetails(data);
      } catch (err) {
        if (axios.isAxiosError(err)) {
          setError(err.response?.data?.detail || "Failed to fetch team details");
        } else {
          setError("An unexpected error occurred");
        }
      }
    };

    if (team_id) {
        if (!isNaN(team_id) && team_id > 0) {
            fetchTeamDetails(team_id);
        }
    }
  }, [team_id]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!teamDetails) {
    return <div>Loading...</div>;
  }

  return (
    <div className="h-screen-less-all-headers relative">
      
      <h2 className="text-xl font-semibold mb-4">{`Team ${teamDetails.team_name}`}</h2>
      <p>Registration Date: {teamDetails.registration_date_ddmm}</p>
      <p>Group Number: {teamDetails.group_number}</p>
      <MatchupHistoryBoard matchupDetails={matchupDetailRows}/>
    </div>
  );
};

export default TeamDetailPage;