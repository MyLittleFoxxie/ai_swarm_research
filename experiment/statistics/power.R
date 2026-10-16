# Rscript statistics/power.R H1 5 1000 0.5 0.10 0.10 output.csv
# H6: baseline=posts/agent, ICC argument unused, effect=1.25, dispersion optional.
# H5: baseline=row probability; respects one volunteer per request (no fictitious independent winners).
args <- commandArgs(trailingOnly=TRUE)
if(length(args)<7) stop("Arguments: H1..H6 seeds replicates baseline ICC effect output.csv [dispersion]")
script <- sub("^--file=","",grep("^--file=",commandArgs(),value=TRUE)[1])
source(file.path(dirname(script),"models.R"))
h<-args[1]; seeds<-as.integer(args[2]); reps<-as.integer(args[3]); p0<-as.numeric(args[4]); icc<-as.numeric(args[5]); effect<-as.numeric(args[6])
dispersion<-if(length(args)>7) as.numeric(args[8]) else 1
stopifnot(h %in% paste0("H",1:6),seeds>0,reps>0,icc>=0,icc<1)
if(h=="H5" && (p0+effect)*24>1) stop("H5 target exceeds single-winner row-rate ceiling; revise target before simulating")
set.seed(12345)
source(file.path(dirname(script),"design.R"))

results<-vector("list",reps)
for(i in seq_len(reps)) {
  result<-tryCatch(primary_contrast(h,fit_primary(h,simulate_design(h,seeds,p0,icc,effect,dispersion))),error=function(e) list(error=conditionMessage(e)))
  results[[i]]<-data.frame(replicate=i,p=if(is.null(result$p)) NA_real_ else result$p,
                           singular=if(is.null(result$singular)) NA else result$singular,
                           failure=if(is.null(result$error)) "" else result$error)
}
result<-do.call(rbind,results)
result$rejected<-!is.na(result$p) & result$p<.05/6 # Failed fits count as non-rejections.
write.csv(result,args[7],row.names=FALSE)
power<-mean(result$rejected); se<-sqrt(power*(1-power)/reps)
write.csv(data.frame(hypothesis=h,seeds=seeds,replicates=reps,assumed_baseline=p0,assumed_icc=icc,
                     assumed_effect=effect,assumed_dispersion=dispersion,power=power,mc_se=se,
                     failures=sum(is.na(result$p)),status="synthetic_planning_not_study_results"),
          paste0(args[7],".summary.csv"),row.names=FALSE)
