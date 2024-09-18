import React, { KeyboardEventHandler, useRef, useState } from 'react'
import { BatchCreateMatchResultsRequest, CreateMatchResults, CreateMatchResultsSchema, MatchResultBase } from '../../types/match';
import { z } from 'zod';


const CreateMatchResult = () => {
    const [lineStack, setLineStack] = useState<string[]>([]);
    const [currentLine, setCurrentLine] = useState<string>('');
    const linePassesRef = useRef<boolean>(false);
    // const [roundNumber, setRoundNumber] = useState<number>(1);
    const roundNumber = 1;

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const payload: BatchCreateMatchResultsRequest = {
            results:[],
            round_number:roundNumber
        }

        const lines: string[] = inputValue.split("\n");

        lines.forEach((line:string)=>{
            const splitLine = line.trim().split(" ")
            if (splitLine.length != 4){
                console.log("error", "not length 4")
                return
            }
            const [teamOne, teamTwo, teamOneGoals, teamTwoGoals] = [splitLine[0], splitLine[1], Number(splitLine[2]),Number(splitLine[3])];
            const teamOneMatchResultBase: MatchResultBase = {
                team_name: teamOne,
                goals_scored: teamOneGoals
            }
            const teamTwoMatchResultBase: MatchResultBase = {
                team_name: teamTwo,
                goals_scored: teamTwoGoals
            }
            const createMatchResult: CreateMatchResults = {
                result:[
                    teamOneMatchResultBase,
                    teamTwoMatchResultBase
                ]
            }
            try{
                CreateMatchResultsSchema.parse(createMatchResult)
            } catch (err){
                if (err instanceof z.ZodError) {
                    console.log(err.issues);
                    return
                  }
            }
            // passed
            payload.results.push(createMatchResult)
        })
        if (payload.results.length === 0) {
            // is empty
            return
        }
        
        try {
            console.log(payload)
            const response = await fetch('http://localhost:8000/match_results/', {
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
                console.log(await response.json())
              alert('Failed to submit the form');
            }
          } catch (error) {
            console.error('Error submitting the form:', error);
            alert('An error occurred while submitting the form');
          }
        };
        const handleKeyDown = (event:React.KeyboardEvent<HTMLTextAreaElement>) =>{
            if (event.key === 'Enter'){
                linePassesRef.current = false
                const splitLine = currentLine.trim().split(" ")
                if (splitLine.length != 4){
                    console.log("error", "not length 4")
                    return
                }
                const [teamOne, teamTwo, teamOneGoals, teamTwoGoals] = [splitLine[0], splitLine[1], Number(splitLine[2]),Number(splitLine[3])];
                const teamOneMatchResultBase: MatchResultBase = {
                    team_name: teamOne,
                    goals_scored: teamOneGoals
                }
                const teamTwoMatchResultBase: MatchResultBase = {
                    team_name: teamTwo,
                    goals_scored: teamTwoGoals
                }
                const createMatchResult: CreateMatchResults = {
                    result:[
                        teamOneMatchResultBase,
                        teamTwoMatchResultBase
                    ]
                }
                try{
                    CreateMatchResultsSchema.parse(createMatchResult)
                    linePassesRef.current = true
                } catch (err){
                    if (err instanceof z.ZodError) {
                        console.log(err.issues);
                    }
                }
                if (linePassesRef.current === true){
                    setLineStack(lineStack => lineStack.concat(currentLine))
                }
            } else if (event.key === 'Backspace' && currentLine.length == 0 && lineStack.length>0){
                const curLineStack = lineStack
                setCurrentLine(curLineStack.pop()!)
                setLineStack(curLineStack)
            }
        }
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="message">Enter your message:</label>
        <textarea
          id="message"
          name="message"
          value={lineStack.join('\n') + (lineStack.length>0?'\n':'') + currentLine}
          onKeyDown={e=>{handleKeyDown(e)}}
          onChange={(e) => {
            let curFullTextValue = e.target.value
            if (linePassesRef.current === false){
                curFullTextValue = curFullTextValue.replace(/\n$/g,'')
            }
            const lines = curFullTextValue.split('\n')
            setCurrentLine(lines[lines.length-1]);
        }
        }
          rows={4}
          cols={50}
          placeholder="<Team name one> <Team name two> <Team one goals> <Team two goals> for each line"
        />
      </div>
      <button type="submit">Submit</button>
    </form>
  )
}

export default CreateMatchResult