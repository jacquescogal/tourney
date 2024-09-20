import React, { useEffect, useRef, useState } from "react";
import {
  BatchCreateMatchResultsRequest,
  CreateMatchResults,
  CreateMatchResultsSchema,
  MatchResultBase,
  MatchResultBaseSchema,
} from "../../types/match";
import { z } from "zod";
import Button from "../commons/Button";
import { Result } from "../../types/generic";
import MatchService from "../../api/MatchService";

const CreateMatchResultForm = (props:{consoleText:string, appendToConsole:(text: string) => void, content:React.ReactNode}) => {
  const [text, setText] = useState("");
  const [counter, setCounter] = useState<number>(0); // forces re-render
  const [showPopup, setShowPopup] = useState<boolean>(false);
  const consoleRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlightRef = useRef<HTMLDivElement>(null);
  const roundNumber = 1;


  const getCursorLineNumber = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      const cursorPosition = textarea.selectionStart;
      const textBeforeCursor = textarea.value.substring(0, cursorPosition);
      const lineNumber = textBeforeCursor.split("\n").length;
      return lineNumber;
    }
    return 0;
  };

  const getResultIfLinePass = (line: string): Result<CreateMatchResults> => {
    const splitLine = line.trim().split(/\s+/);
    if (splitLine.length != 4) {
      return { error: new Error("not length 4") };
    }
    const [teamOne, teamTwo, teamOneGoals, teamTwoGoals] = [
      splitLine[0],
      splitLine[1],
      Number(splitLine[2]),
      Number(splitLine[3]),
    ];
    const teamOneMatchResultBase: MatchResultBase = {
      team_name: teamOne,
      goals_scored: teamOneGoals,
    };
    const teamTwoMatchResultBase: MatchResultBase = {
      team_name: teamTwo,
      goals_scored: teamTwoGoals,
    };
    const createMatchResult: CreateMatchResults = {
      result: [teamOneMatchResultBase, teamTwoMatchResultBase],
    };
    try {
      CreateMatchResultsSchema.parse(createMatchResult);
    } catch (err) {
      if (err instanceof z.ZodError) {
        console.log(err.issues);
        return { error: err };
      }
    }

    return { value: createMatchResult };
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const payload: BatchCreateMatchResultsRequest = {
      results: [],
      round_number: roundNumber,
    };

    const lines: string[] = text.split("\n");

    lines.forEach((line: string) => {
      // passed
      const result = getResultIfLinePass(line);
      if ("value" in result) {
        payload.results.push(result.value);
      }
    });
    if (payload.results.length === 0) {
      // is empty
      return;
    }

    try {
      const response = await MatchService.createMatchResults(payload);
      if (response.ok) {
        props.appendToConsole(
          "body:\n" + JSON.stringify(payload) + "\nServer Response:\nsuccess"
        );
        setText(""); // Reset the form
      } else {
        const jsonData = await response.json();
        props.appendToConsole(
          "body:\n" +
            JSON.stringify(payload) +
            "\nServer Response:\nerror:" +
            JSON.stringify(jsonData)
        );
      }
    } catch (error) {
      props.appendToConsole(
        "body:\n" +
          JSON.stringify(payload) +
          "\nServer Response:\nerror:\n " +
          error
      );
    }
  };

  // Function to highlight
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const getHighlightedText = (text: string, _counter: number) => {
    // split into lines
    const splitBy = "\n";
    const splitText = text.split(splitBy);
    return splitText.map((line, index) => {
      const errorArray: string[] = [];
      // queue checks
      const strippedLine = line.trim();
      // split by whitespace of variable length
      const splitLine = strippedLine.split(/\s+/);
      if (splitLine[0].length === 0) {
        splitLine.shift();
      }
      // check if the line has 4 elements
      if (splitLine.length > 4) {
        errorArray.push("❌ expected 4 args only");
      } else if (splitLine.length <= 3) {
        if (splitLine.length > 0) {
          const teamOne = splitLine[0];
          try {
            MatchResultBaseSchema.shape.team_name.parse(teamOne);
          } catch (err) {
            if (err instanceof z.ZodError) {
              errorArray.push(`❌ ${err.issues[0].message}`);
            }
          }
        }
        if (splitLine.length > 1) {
          const teamTwo = splitLine[1];
          try {
            MatchResultBaseSchema.shape.team_name.parse(teamTwo);
          } catch (err) {
            if (err instanceof z.ZodError) {
              errorArray.push(`❌ ${err.issues[0].message}`);
            }
          }
        }

        if (splitLine.length > 2) {
          const teamOneGoals = Number(splitLine[2]);
          try {
            MatchResultBaseSchema.shape.goals_scored.parse(teamOneGoals);
          } catch (err) {
            if (err instanceof z.ZodError) {
              errorArray.push(`❌ ${err.issues[0].message}`);
            }
          }
        }

        if (splitLine.length > 3) {
          const teamTwoGoals = Number(splitLine[3]);
          try {
            MatchResultBaseSchema.shape.goals_scored.parse(teamTwoGoals);
          } catch (err) {
            if (err instanceof z.ZodError) {
              errorArray.push(`❌ ${err.issues[0].message}`);
            }
          }
        }
        if (splitLine.length === 0) {
          errorArray.push("<team one name>");
        }
        if (splitLine.length <= 1) {
          errorArray.push("<team two name>");
        }
        if (splitLine.length <= 2) {
          errorArray.push("<team one goals>");
        }
        if (splitLine.length <= 3) {
          errorArray.push("<team two goals>");
        }
      }
      const cursorLineNumber = getCursorLineNumber();
      return errorArray.length === 0 ? (
        <>
          <span key={index} className="bg-green-400 rounded p-[3px]">
            {line}
          </span>
          {cursorLineNumber === index + 1 ? (
            <span className="absolute bg-white z-[100] text-black mx-2 p-1 outline outline-1 text-[10px] text-nowrap   rounded">
              ✅ correct format
            </span>
          ) : (
            <span className="absolute bg-white z-[1] text-black mx-2 p-1  text-[10px] text-nowrap   rounded">
              ✅
            </span>
          )}

          {splitBy}
        </>
      ) : (
        <>
          <span key={index} className="bg-red-400 rounded p-[3px]">
            {line}
          </span>
          {cursorLineNumber === index + 1 && showPopup ? (
            <span className=" absolute z-[100] bg-white fixed text-black mx-2 p-1 outline outline-1 text-[10px]  rounded">
              {errorArray.join("\n")}
            </span>
          ) : (
            <span className=" absolute bg-white fixed text-black mx-2 p-1  text-[10px]  rounded">
              ❌
            </span>
          )}

          {splitBy}
        </>
      );
    });
  };
  // Synchronize scroll of textarea and highlight div
  const handleScroll = () => {
    if (highlightRef.current && textareaRef.current) {
      highlightRef.current.scrollTop = textareaRef.current.scrollTop;
      highlightRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [props.consoleText]);
  return (
    <div className="h-screen-less-all-headers w-article-wide flex flex-col ">
      {props.content}
    <form
      onSubmit={handleSubmit}
      className="bg-blue-100 flex justify-center flex-col w-full items-center p-4 rounded-lg"
    >
      <h1 className="text-2xl self-start text-text-pop">Console</h1>
      <div
        ref={consoleRef}
        className="bg-black text-green-300 p-2 h-[200px] w-full overflow-y-scroll whitespace-pre-wrap break-words scroll-smooth"
      >
        {props.consoleText}
      </div>
      <h1 className="text-2xl self-start text-text-pop">Create Matchup</h1>
      {/* format */}
      <body className="text-xs self-start text-text-norm">
        Format: {"<"}team_one_name{">"} {"<"}team_two_name{">"} {"<"}
        team_one_goals{">"} {"<"}team_two_goals{">"} {" "}
      </body>
      <body className="text-xs self-start text-text-norm">
        Transaction is atomic
      </body>
      <div style={{ position: "relative", width: "100%", height: "200px" }}>
        {/* The overlay div with highlighted text */}
        <div
          ref={highlightRef}
          className="absolute w-full h-full p-[8px] bg-white color-transparent whitespace-pre-wrap break-words overflow-y-auto pointer-events-none resize-none"
        >
          <div style={{ color: "transparent", whiteSpace: "pre-wrap" }}>
            {text.length > 0 && getHighlightedText(text, counter)}
          </div>
        </div>

        {/* The textarea itself for editing */}
        <div className="border border-black w-full h-[200px] relative">
          <textarea
            ref={textareaRef}
            className="w-full h-full absolute top-0 left-0 p-[8px] bg-transparent text-black whitespace-pre-wrap break-words  resize-none"
            value={text}
            onClick={() => {
              setCounter((counter) => counter + 1);
              setShowPopup(true);
            }}
            onKeyUp={()=>{
                setCounter((counter) => counter + 1);
              }}
            onBlur={() => {
              setShowPopup(false);
            }}
            onChange={(e) => setText(e.target.value)}
            onScroll={handleScroll}
            placeholder="<team_one_name> <team_two_name> <team_one_goals> <team_two_goals>"
          />
        </div>
      </div>
      <Button
        onClick={() => {
          console.log("clicked");
        }}
      >
        Submit
      </Button>
    </form>
  </div>
  );
};

export default CreateMatchResultForm;
