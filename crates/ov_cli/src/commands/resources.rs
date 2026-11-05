use crate::client::HttpClient;
use crate::error::Result;
use crate::output::{OutputFormat, output_success};
use serde_json::{Map, Value};

pub async fn add_resource(
    client: &HttpClient,
    path: &str,
    add_type: Option<String>,
    to: Option<String>,
    parent: Option<String>,
    parent_auto_create: Option<String>,
    reason: String,
    instruction: String,
    wait: bool,
    timeout: Option<f64>,
    strict: bool,
    ignore_dirs: Option<String>,
    include: Option<String>,
    exclude: Option<String>,
    directly_upload_media: bool,
    watch_interval: f64,
    processing_mode: String,
    resource_args: Option<Map<String, Value>>,
    tags: Vec<String>,
    tag_mode: String,
    confidence: Option<f64>,
    format: OutputFormat,
    compact: bool,
    show_progress: bool,
    verbose: bool,
) -> Result<()> {
    let result = client
        .add_resource(
            path,
            add_type,
            to,
            parent,
            parent_auto_create,
            &reason,
            &instruction,
            wait,
            timeout,
            strict,
            ignore_dirs,
            include,
            exclude,
            directly_upload_media,
            watch_interval,
            processing_mode,
            resource_args,
            tags,
            tag_mode,
            confidence,
            show_progress,
            verbose,
        )
        .await?;

    if !wait && matches!(format, OutputFormat::Table) {
        eprintln!("Note: Resource is being processed in the background.");
        eprintln!(
            "Use 'ov task status <task_id>' to check progress, or 'ov task list' to see all tasks."
        );
    }

    let effective_confidence = confidence.unwrap_or(1.0);
    let mut result = result;
    match format {
        // The table renderer prints every key of an object result, so the human
        // readable echo goes on its own stdout line instead of into the body.
        OutputFormat::Table => println!("{}", render_confidence_line(confidence)),
        // JSON consumers read the effective value from the payload itself.
        OutputFormat::Json => merge_confidence_into_result(&mut result, effective_confidence),
    }

    output_success(&result, format, compact);
    Ok(())
}

/// Effective confidence echoed after an import: the explicit value, or the
/// default that the server will apply when the flag was omitted.
fn render_confidence_line(confidence: Option<f64>) -> String {
    let effective_confidence = confidence.unwrap_or(1.0);
    match confidence {
        Some(value) => format!("confidence {value:.3}"),
        None => format!("confidence {effective_confidence:.3} (default)"),
    }
}

fn merge_confidence_into_result(result: &mut Value, effective_confidence: f64) {
    if let Some(object) = result.as_object_mut() {
        object.insert("confidence".to_string(), serde_json::json!(effective_confidence));
    }
}

pub async fn add_skill(
    client: &HttpClient,
    data: &str,
    wait: bool,
    timeout: Option<f64>,
    parent: Option<&str>,
    show_progress: bool,
    verbose: bool,
    format: OutputFormat,
    compact: bool,
) -> Result<()> {
    let result = client
        .add_skill(data, wait, timeout, show_progress, verbose, None, parent)
        .await?;

    if !wait && matches!(format, OutputFormat::Table) {
        eprintln!("Note: Skill is being processed in the background.");
        eprintln!(
            "Use 'ov task status <task_id>' to check progress, or 'ov task list' to see all tasks."
        );
    }

    output_success(&result, format, compact);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn render_confidence_line_explicit_value() {
        let line = render_confidence_line(Some(0.4));

        assert_eq!(line, "confidence 0.400");
        assert!(!line.contains("(default)"));
    }

    #[test]
    fn render_confidence_line_default_value() {
        let line = render_confidence_line(None);

        assert!(line.contains("(default)"));
        assert_eq!(line, "confidence 1.000 (default)");
    }

    #[test]
    fn merge_confidence_into_json_result() {
        let mut result = json!({"task_id": "task-1", "status": "accepted"});

        merge_confidence_into_result(&mut result, 0.4);

        assert_eq!(result["confidence"], json!(0.4));
        assert_eq!(result["task_id"], json!("task-1"));
        assert_eq!(result["status"], json!("accepted"));
    }
}
