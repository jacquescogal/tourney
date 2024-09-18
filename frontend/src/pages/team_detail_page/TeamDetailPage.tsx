import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { ITeamDetails, ITeamMatchUpDetail, ITeamMatchUpDetailRow } from "../../types/team";
import TeamService from "../../api/teamService";
import MatchupHistoryBoard from "../../components/boards/MatchupHistoryBoard";

const TeamDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [teamDetails, setTeamDetails] = useState<ITeamDetails | null>(null);
  const [matchupDetailRows, setMatchupDetailRows] = useState<ITeamMatchUpDetailRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch team data from the API
  useEffect(() => {
    const fetchTeamDetails = async (team_id:number) => {
      try {
        const data = await TeamService.fetchTeamDetailPage(team_id);
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

    if (id) {
        const team_id = Number(id);
        if (!isNaN(team_id)){
            fetchTeamDetails(team_id);
        }
    }
  }, [id]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!teamDetails) {
    return <div>Loading...</div>;
  }

  return (
    <div className="h-screen-less-header relative">
      <h1>Team Details for {teamDetails.team_name}</h1>
      <p>Registration Date: {teamDetails.registration_date_ddmm}</p>
      <p>Group Number: {teamDetails.group_number}</p>
      <MatchupHistoryBoard matchupDetails={matchupDetailRows}/>
    </div>
  );
};

export default TeamDetailPage;