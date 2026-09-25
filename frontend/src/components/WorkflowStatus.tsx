type WorkflowStatusProps = {
  message: string;
  tone: "info" | "success" | "error";
};

function WorkflowStatus({ message, tone }: WorkflowStatusProps) {
  return (
    <div
      className={`workflow-status ${tone}`}
      role={tone === "error" ? "alert" : "status"}
    >
      {message}
    </div>
  );
}

export default WorkflowStatus;
