import React, { useState } from 'react'
import { BatchRegisterTeamRequest, RegisterTeamRequest, RegisterTeamRequestSchema } from '../../types/teams';
import { z } from 'zod';


const CreateTeam = () => {
    const [inputValue, setInputValue] = useState<string>('');

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const payload:BatchRegisterTeamRequest = {
            teams:[]
        }

        const lines: string[] = inputValue.split("\n");

        lines.forEach((line:string)=>{
            const splitLine = line.trim().split(" ")
            if (splitLine.length != 3){
                console.log("error", "not length 3")
                return
            }
            const [teamName, registrationDate, groupNumber] = [splitLine[0], splitLine[1], Number(splitLine[2])];
            const registrationTeamRequest: RegisterTeamRequest = {
                team_name: teamName,
                registration_date: registrationDate,
                group_number: groupNumber
            }
            try{
                RegisterTeamRequestSchema.parse(registrationTeamRequest)
            } catch (err){
                if (err instanceof z.ZodError) {
                    console.log(err.issues);
                    return
                  }
            }
            // passed
            payload.teams.push(registrationTeamRequest)
        })
        if (payload.teams.length === 0){
            return
        }
        
        try {
            const response = await fetch('http://localhost:8000/teams/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(payload),
            });
      
            if (response.ok) {
              alert('Form submitted successfully!');
              setInputValue('');  // Reset the form
            } else {
              alert('Failed to submit the form');
            }
          } catch (error) {
            console.error('Error submitting the form:', error);
            alert('An error occurred while submitting the form');
          }
        };
    
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="message">Enter your message:</label>
        <textarea
          id="message"
          name="message"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          rows={4}
          cols={50}
          placeholder="<Team name> <Registration date in DD/MM> <Group number> for each line"
        />
      </div>
      <button type="submit">Submit</button>
    </form>
  )
}

export default CreateTeam